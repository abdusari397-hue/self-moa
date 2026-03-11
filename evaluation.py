import os
import time
import csv
import re
from typing import Dict, Any
from openai import OpenAI
from self_moa_pipeline import generate_drafts, aggregate_drafts, MODEL

# Setup client (Using the model specified in self_moa_pipeline)
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY", "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"),
    base_url=os.environ.get("OPENAI_BASE_URL", "https://openrouter.ai/api/v1") 
)

# Mock Cost Constants for Qwen 3.5 Flash (example format: $ per 1K tokens)
COST_PER_1K_IN_TOKENS = 0.0005
COST_PER_1K_OUT_TOKENS = 0.0015

def estimate_tokens(text: str) -> int:
    """A rough heuristic to estimate tokens (~4 chars per token)."""
    return len(str(text)) // 4

def calculate_cost(input_tokens: int, output_tokens: int) -> float:
    """Calculate the estimated cost of an API call."""
    in_cost = (input_tokens / 1000.0) * COST_PER_1K_IN_TOKENS
    out_cost = (output_tokens / 1000.0) * COST_PER_1K_OUT_TOKENS
    return in_cost + out_cost

# --- Evaluation Execution Modes ---

def run_baseline(prompt: str) -> Dict[str, Any]:
    """Base mode: Sends the prompt to the model directly without MoA architecture."""
    start_time = time.time()
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        output = response.choices[0].message.content
        
        # OpenRouter/OpenAI usually provides usage stats
        in_tokens = response.usage.prompt_tokens if response.usage else estimate_tokens(prompt)
        out_tokens = response.usage.completion_tokens if response.usage else estimate_tokens(output)
    except Exception as e:
        output = f"Error during baseline execution: {e}"
        in_tokens, out_tokens = 0, 0
        
    latency = time.time() - start_time
    total_tokens = in_tokens + out_tokens
    cost = calculate_cost(in_tokens, out_tokens)
    
    return {"output": output, "latency": latency, "tokens": total_tokens, "cost": cost}

def run_moa(prompt: str, num_drafts: int) -> Dict[str, Any]:
    """MoA mode: Generates drafts concurrently, then aggregates them using a single pass."""
    start_time = time.time()
    
    # Generate Drafts (Stage 1 & 2) with fixed temperature 0.7 to avoid hallucinations
    drafts = generate_drafts(prompt, num_drafts=num_drafts, temperatures=[0.7])
    
    if not drafts or all(d.startswith("Error") for d in drafts):
        return {"output": "Error: Failed to generate drafts.", "latency": time.time() - start_time, "tokens": 0, "cost": 0.0}

    # Aggregate Drafts (Stage 3)
    criteria = "Ensure the response is mathematically and logically sound, accurate, complete, well-formatted, and prioritizes quality."
    final_output = aggregate_drafts(prompt, drafts, criteria=criteria)
    
    latency = time.time() - start_time
    
    # Estimate total token usage for the entire MoA pipeline
    # Draft Generation Tokens: (prompt length * num_drafts) + total length of drafts
    drafts_in_tokens = estimate_tokens(prompt) * num_drafts
    drafts_out_tokens = sum(estimate_tokens(d) for d in drafts)
    
    # Aggregation Tokens: (All drafts + prompt + system prompt) + final output
    agg_in_tokens = drafts_out_tokens + estimate_tokens(prompt) + 200 # 200 for system prompt/criteria
    agg_out_tokens = estimate_tokens(final_output)
    
    total_in = drafts_in_tokens + agg_in_tokens
    total_out = drafts_out_tokens + agg_out_tokens
    total_tokens = total_in + total_out
    cost = calculate_cost(total_in, total_out)
    
    return {"output": final_output, "latency": latency, "tokens": total_tokens, "cost": cost}

# --- LLM-as-a-Judge Scoring ---

def evaluate_with_llm(prompt: str, response: str) -> int:
    """Uses LLM-as-a-Judge to score the response from 1 to 10."""
    judge_prompt = f"""
    You are an impartial and expert judge. Please evaluate the quality of the following response to the user's prompt.
    Rate the response strictly on a scale of 1 to 10, where 10 is absolutely perfect, flawless logically, and structurally sound.
    Consider accuracy, completeness, reasoning, and adherence to the prompt.
    Provide ONLY the integer score as your output, nothing else.

    User Prompt:
    {prompt}

    Response to Evaluate:
    {response}
    """
    try:
        res = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": judge_prompt}],
            temperature=0.0,
        )
        score_str = res.choices[0].message.content.strip()
        # Extract the first number found to prevent parsing errors
        match = re.search(r'\d+', score_str)
        if match:
             score = int(match.group())
             return min(10, max(1, score)) # Ensure it's between 1 and 10
        return 5 # Fallback score
    except Exception as e:
        print(f"❌ Evaluation error: {e}")
        return 0

# --- Main Benchmark Execution ---

def main():
    # Dataset modified to defeat the 'Ceiling Effect' with extremely hard prompts
    # Removed creative tasks as Self-MoA merges competing creative visions into a mess
    dataset = [
        {
            "id": "reasoning_hard", 
            "category": "Reasoning", 
            "prompt": "Five pirates of different ages have a treasure of 100 gold coins. On their ship, they decide to split the coins using this scheme: The oldest pirate proposes how to share the coins, and ALL pirates (including the oldest) vote for or against it. If 50% or more of the pirates vote for it, then the coins will be shared that way. Otherwise, the pirate proposing the scheme will be thrown overboard, and the process is repeated with the pirates that remain. As pirates tend to be a bloodthirsty bunch, if a pirate would get the same number of coins if he voted for or against a proposal, he will vote against it so that the proposer is thrown overboard. Assuming that all 5 pirates are perfectly intelligent, rational, greedy, and do not wish to die, what will the oldest pirate propose?"
        },
        {
            "id": "coding_hard", 
            "category": "Coding", 
            "prompt": "Write a highly optimized Python implementation of the A* search algorithm for a 3D grid with non-uniform traversal costs, incorporating a custom priority queue that handles dynamic weight updates without total re-sorting. Provide Big-O analysis for time and space complexity."
        }
    ]

    results = []
    
    print("\n" + "="*60)
    print("🔬 Starting Global Benchmark Evaluation For Self-MoA")
    print("="*60 + "\n")

    for task in dataset:
        print(f"📝 Testing Task [{task['id']}] - Category: {task['category']}")
        print("-" * 40)
        
        # Define the modes to evaluate
        execution_modes = [
            ("Baseline", lambda p: run_baseline(p)),
            ("MoA-4", lambda p: run_moa(p, 4)),
            ("MoA-8", lambda p: run_moa(p, 8))
        ]

        for mode_name, execute_func in execution_modes:
            print(f"   ▶ Running {mode_name}...")
            
            # 1. Execute Mode
            res = execute_func(task['prompt'])
            
            # 2. Evaluate with Judge
            if res['output'].startswith("Error"):
                score = 0
                print(f"      ❌ Failed execution. Assigning score 0.")
            else:
                print(f"   ⚖️ Evaluating {mode_name} with LLM Judge...")
                score = evaluate_with_llm(task['prompt'], res['output'])
            
            # 3. Store Results
            results.append({
                "task_id": task['id'],
                "category": task['category'],
                "mode": mode_name,
                "latency_seconds": round(res['latency'], 2),
                "total_tokens": res['tokens'],
                "estimated_cost_usd": round(res['cost'], 5),
                "quality_score": score
            })
            
            print(f"      📈 Result -> Score={score}/10 | Latency={res['latency']:.1f}s | Cost=${res['cost']:.5f}\n")

    # Final Export
    csv_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evaluation_results.csv")
    print(f"\n💾 Saving all results to: {csv_filename}")
    
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print("\n✅ Evaluation complete. You can now analyze the CSV and plot the graphs!")

if __name__ == "__main__":
    main()
