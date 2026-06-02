import os
import re
import json
import sys
import matplotlib.pyplot as plt
import numpy as np
from self_moa_pipeline import get_client, MODEL

# Force UTF-8 encoding for standard output to support emojis/Arabic in Windows terminal
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

# تهيئة العميل للاتصال بـ OpenRouter
client = get_client()

JUDGE_MODEL = os.environ.get("JUDGE_MODEL", MODEL) # Default to dynamic Qwen model to save cost, can be overridden

def evaluate_and_chart(file_path="benchmark_results.md"):
    print("⚖️ Initiating LLM-as-a-Judge with Visual Analytics...")
    
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            benchmark_data = file.read()
    except FileNotFoundError:
        return "Error: Could not find benchmark_results.md"

    judge_prompt = f"""
    You are an impartial and expert AI Judge evaluating a benchmark comparing 'Single-Pass Claude Opus' (SP) and a 'Self-MoA Pipeline' (MoA).
    
    Here is the benchmark report:
    
    {benchmark_data}
    
    **Evaluation Criteria (Score out of 10 for each):**
    1. Accuracy (Is the final answer correct?)
    2. Reasoning Quality (Logical flow, explicit deduction, no leaps.)
    3. Formatting & Readability (Use of tables, headers, clear synthesis.)
    
    **Output Requirement:**
    You must output ONLY valid JSON format containing the scores averaged across all questions. No markdown, no explanations. Use this exact schema:
    {{
        "scores": {{
            "Accuracy": {{"Claude Opus": <number>, "Self-MoA": <number>}},
            "Reasoning Quality": {{"Claude Opus": <number>, "Self-MoA": <number>}},
            "Formatting & Readability": {{"Claude Opus": <number>, "Self-MoA": <number>}}
        }}
    }}
    """

    print("   -> Analyzing answers and extracting JSON scores...")
    
    try:
        response = client.chat.completions.create(
            model=JUDGE_MODEL,
            messages=[{"role": "user", "content": judge_prompt}],
            temperature=0.0
        )
        
        # استخراج الـ JSON
        output = response.choices[0].message.content
        json_match = re.search(r'\{.*\}', output, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0))
        else:
            print("Failed to parse JSON. Raw output:")
            print(output)
            return
            
        print("✅ Scores extracted:", data)
        generate_chart(data["scores"])
        
    except Exception as e:
        print(f"Error during evaluation: {e}")

def generate_chart(scores_data):
    print("📈 Generating Evaluation Chart...")
    
    categories = list(scores_data.keys())
    opus_scores = [scores_data[cat]["Claude Opus"] for cat in categories]
    moa_scores = [scores_data[cat]["Self-MoA"] for cat in categories]

    x = np.arange(len(categories))  # Label locations
    width = 0.35  # Bar width

    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Adding an aesthetic touch 
    ax.set_facecolor('#fdfdfd')
    fig.patch.set_facecolor('#fdfdfd')

    rects1 = ax.bar(x - width/2, opus_scores, width, label='Claude Opus (Single-Pass)', color='#4f8bc9')
    rects2 = ax.bar(x + width/2, moa_scores, width, label='Self-MoA Pipeline', color='#e05d5d')

    ax.set_ylabel('Scores (out of 10)', fontsize=12, fontweight='bold')
    ax.set_title('LLM-as-a-Judge: Self-MoA vs Claude Opus', fontsize=16, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=11)
    ax.legend(fontsize=11)
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Attach a text label above each bar displaying its height
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=10, fontweight='bold')

    autolabel(rects1)
    autolabel(rects2)

    fig.tight_layout()
    chart_filename = "evaluation_chart.png"
    plt.savefig(chart_filename, dpi=300)
    print(f"🎉 Chart successfully saved as '{chart_filename}'!")

if __name__ == "__main__":
    evaluate_and_chart()
