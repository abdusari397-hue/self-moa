import os
import concurrent.futures
import argparse
import sys
from openai import OpenAI
from typing import List, Optional

# Force UTF-8 encoding for standard output to support emojis/Arabic in Windows terminal
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

# Default client configuration
DEFAULT_API_KEY = "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"
DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
MODEL = "qwen/qwen3.5-flash-02-23"

def get_client(api_key: Optional[str] = None, base_url: Optional[str] = None) -> OpenAI:
    """Helper to initialize the OpenAI client with fallback configuration"""
    key = api_key or os.environ.get("OPENAI_API_KEY", DEFAULT_API_KEY)
    url = base_url or os.environ.get("OPENAI_BASE_URL", DEFAULT_BASE_URL)
    return OpenAI(api_key=key, base_url=url)

# --- [Stage 1]: Unifying Roles ---

def generate_single_draft(prompt: str, temperature: float = 0.7, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None) -> str:
    """Generate a single draft from the model"""
    active_model = model or MODEL
    active_client = get_client(api_key, base_url)
    try:
        response = active_client.chat.completions.create(
            model=active_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

def generate_drafts(prompt: str, num_drafts: int = 6, temperatures: List[float] = None, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None) -> List[str]:
    """
    Stage 2: In-model Diversity via Temperature Scaling
    Generates a dynamic number of drafts. The first draft is baseline at temperature 0.0,
    and subsequent drafts are scaled using the provided temperatures.
    """
    if temperatures is None or len(temperatures) == 0:
        temperatures = [0.7]
        
    drafts = []
    print(f"📌 Generating {num_drafts} drafts concurrently...")
    
    # 1 Baseline draft at 0.0, and the remaining (num_drafts - 1) distributed among the temperatures list
    tasks = [0.0]
    if num_drafts > 1:
        for i in range(num_drafts - 1):
            temp_idx = i % len(temperatures)
            tasks.append(temperatures[temp_idx])
            
    tasks = tasks[:num_drafts]
    print(f"   -> Draft temperatures: {tasks}")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_drafts) as executor:
        futures = {executor.submit(generate_single_draft, prompt, temp, api_key, base_url, model): temp for temp in tasks}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if not result.startswith("Error:"):
                drafts.append(result)
            else:
                print(f"❌ {result}")
                
    return drafts

def aggregate_drafts(prompt: str, drafts: List[str], criteria: Optional[str] = None, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None) -> str:
    """
    Stage 3: Single Pass Aggregation & In-Context Reasoning
    Sends all drafts in a single massive context window to act as a Critical Judge.
    """
    print(f"🔄 Performing Single Pass Aggregation on {len(drafts)} drafts (Context Window Processing)...")
    
    active_model = model or MODEL
    active_client = get_client(api_key, base_url)
    
    aggregation_prompt = f"Original User Prompt:\n{prompt}\n\nHere are {len(drafts)} proposed solutions to answer this prompt:\n"
    for i, draft in enumerate(drafts, 1):
        aggregation_prompt += f"\n--- Solution {i} ---\n{draft}\n"
    
    aggregation_prompt += "\nPlease act as a Critical Judge. Carefully analyze and reason about the contradictions and differences between these solutions. Extract the safest, most scalable, and highest-quality design. Synthesize a single, definitive, flawless final answer."

    # Incorporate evaluation criteria into the system prompt if provided
    system_content = "You are an Expert Arbiter and Architect. Your task is to perform advanced in-context reasoning across multiple proposed solutions, resolve conflicting advice logically, and produce the ultimate definitive response."
    if criteria:
        system_content += f"\n\nCRITICAL EVALUATION CRITERIA YOU MUST FOLLOW WHEN SYNTHESIZING:\n{criteria}"

    try:
        response = active_client.chat.completions.create(
            model=active_model,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": aggregation_prompt}
            ],
            temperature=0.0,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error during aggregation: {e}"

# ================= CLI Interface =================

def run_pipeline(prompt: str, num_drafts: int, temperatures: List[float], criteria: str):
    print("\n" + "="*50)
    print("Initiating Self-MoA Execution (2026 Advanced)")
    print("="*50 + "\n")
    
    print("--- [Stages 1 & 2]: Proposing & Temperature Scaling ---")
    drafts = generate_drafts(prompt, num_drafts=num_drafts, temperatures=temperatures)
    
    if not drafts:
        print("Failed to generate drafts. Please check your API configuration or network connection.")
        return

    print("\n--- [Stage 3]: In-Context Reasoning (Single Pass) ---")
    final_answer = aggregate_drafts(prompt, drafts, criteria=criteria)
    
    print("\n" + "="*20 + " Final Answer " + "="*20 + "\n")
    print(final_answer)
    print("\n" + "="*54 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Self-MoA advanced pipeline utilizing qwen-turbo with Temperature Scaling and Single Pass Reasoning.")
    parser.add_argument("--prompt", type=str, help="The prompt to evaluate using the pipeline.")
    parser.add_argument("--drafts", type=int, default=8, help="Number of concurrent drafts to generate.")
    parser.add_argument("--temperatures", type=float, nargs='+', default=[0.7, 0.9], help="List of temperatures to scale diversity across drafts.")
    parser.add_argument("--criteria", type=str, default="Ensure the response is accurate, complete, concise, well-formatted in Markdown, and directly addresses the user's prompt without unnecessary conversational padding. Analyze contradictions in the provided drafts carefully.", help="Specific evaluation criteria to instruct the aggregator.")

    args = parser.parse_args()

    # If prompt is not passed via CLI argument, use a default example or ask for input
    user_prompt = args.prompt
    if not user_prompt:
        if not sys.stdin.isatty():
             user_prompt = sys.stdin.read().strip()
        else:
             user_prompt = "Design a highly secure and scalable microservices architecture for a real-time banking application."
             print("ℹ️ No prompt provided. Using default example prompt.")

    run_pipeline(prompt=user_prompt, num_drafts=args.drafts, temperatures=args.temperatures, criteria=args.criteria)
