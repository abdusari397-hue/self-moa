import os
import argparse
import sys
from self_moa_pipeline import generate_drafts, aggregate_drafts, get_client

# Force UTF-8 encoding for standard output to support emojis/Arabic in Windows terminal
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

client = get_client()

CLAUDE_OPUS_MODEL = os.environ.get("BENCHMARK_MODEL", "anthropic/claude-3-opus")

HARD_LOGIC_QUESTIONS = [
    {
        "name": "Cheryl's Birthday",
        "prompt": "Albert and Bernard just became friends with Cheryl, and they want to know when her birthday is. Cheryl gives them a list of 10 possible dates: May 15, May 16, May 19, June 17, June 18, July 14, July 16, August 14, August 15, August 17. Cheryl then tells Albert and Bernard separately the month and the day of her birthday respectively. Albert says: 'I don't know when Cheryl's birthday is, but I know that Bernard doesn't know too.' Bernard says: 'At first I don't know when Cheryl's birthday is, but I know now.' Albert says: 'Then I also know when Cheryl's birthday is.' So when is Cheryl's birthday? Explain your step-by-step logic."
    },
    {
        "name": "The Zebra Puzzle (Einstein's Riddle) - No Options",
        "prompt": "There are five houses in a row, each of a different color. In each house lives a person with a different nationality. These five owners drink a certain type of beverage, smoke a certain brand of cigar, and keep a certain pet. No owners have the same pet, smoke the same brand of cigar, or drink the same beverage. Clues: 1. The Brit lives in the red house. 2. The Swede keeps dogs. 3. The Dane drinks tea. 4. The green house is just to the left of the white house. 5. The green house owner drinks coffee. 6. Pall Mall smoker keeps birds. 7. Yellow house owner smokes Dunhill. 8. Center house owner drinks milk. 9. Norwegian lives in the first house. 10. Blends smoker lives next to cats. 11. Horse keeper lives next to Dunhill smoker. 12. Bluemasters smoker drinks beer. 13. German smokes Prince. 14. Norwegian lives next to the blue house. 15. Blends smoker has a neighbor who drinks water. Question: Who owns the fish?"
    },
    {
        "name": "BIG-bench Hard: Penguins in a Table",
        "prompt": "Here is a table where the first line is a header and each subsequent line is a penguin:  name, age, height (cm), weight (kg) Louis, 7, 50, 11 Bernard, 5, 80, 13 Vincent, 9, 60, 11 Gwen, 8, 70, 15  For example, the age of Louis is 7, the weight of Gwen is 15 kg, the height of Bernard is 80 cm.  We now add a penguin to the table: James, 12, 90, 12  How many penguins are less than 8 years old? Think step-by-step."
    },
    {
         "name": "BIG-bench Hard: Tracking Shuffled Objects",
         "prompt": "Alice, Bob, and Claire are playing a game. At the start of the game, they are each holding a ball: Alice has a yellow ball, Bob has a blue ball, and Claire has a pink ball.  As the game progresses, pairs of players trade balls. First, Claire and Alice swap balls. Then, Alice and Bob swap balls. Finally, Claire and Bob swap balls. At the end of the game, Bob has the yellow ball. True or False? Let's think step by step, tracking the state of each player's ball."
    },
    {
        "name": "LogiQA: Deductive Reasoning",
        "prompt": "In a certain company, if an employee is a manager, they must have a master's degree. If an employee has a master's degree, they must be fluent in at least two languages. Not all employees who are fluent in at least two languages are managers. John is an employee in this company who is fluent in three languages. Based on this information, which of the following MUST be true? (Provide a completely logical deduction for your conclusion instead of picking a letter). A) John is a manager. B) John has a master's degree. C) It is impossible to determine if John is a manager or has a master's degree based solely on this information. D) John is not a manager."
    }
]

def run_claude_opus(prompt: str) -> str:
    print(f"🤖 Running Standard {CLAUDE_OPUS_MODEL} (Zero-Shot)...")
    try:
        response = client.chat.completions.create(
            model=CLAUDE_OPUS_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

def run_self_moa(prompt: str) -> str:
    print("🧠 Running Self-MoA Pipeline...")
    drafts = generate_drafts(prompt, num_drafts=6, temperatures=[0.7])
    if not drafts:
        return "Self-MoA Failed to generate drafts."
    final_answer = aggregate_drafts(prompt, drafts)
    return final_answer

def run_benchmark():
    print("="*60)
    print("🏆 BATTLE OF THE TITANS: SELF-MOA vs CLAUDE OPUS 🏆")
    print("="*60 + "\n")
    
    with open("benchmark_results.md", "w", encoding="utf-8") as f:
        f.write("# Benchmark Results: Self-MoA vs Claude Opus\n\n")
        
        for q in HARD_LOGIC_QUESTIONS:
            print(f"\n▶️ Testing Question: {q['name']}")
            print("-"*60)
            f.write(f"## Question: {q['name']}\n\n**Prompt:**\n> {q['prompt']}\n\n")
            
            # 1. Claude Opus
            opus_answer = run_claude_opus(q['prompt'])
            f.write(f"### 🤖 Single-Pass Claude Opus ({CLAUDE_OPUS_MODEL})\n\n{opus_answer}\n\n")
            
            # 2. Self-MoA
            moa_answer = run_self_moa(q['prompt'])
            f.write(f"### 🧠 Self-MoA Pipeline\n\n{moa_answer}\n\n")
            f.write("---\n\n")
            
            print("✅ Done with this question.\n")
            
    print("\n🎉 Benchmark Complete! Results saved to `benchmark_results.md`🎉")

if __name__ == "__main__":
    run_benchmark()
