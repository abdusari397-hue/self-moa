import sys
import os

# Ensure the current directory is in the path so we can import our pipeline
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from self_moa_pipeline import generate_drafts, aggregate_drafts

def solve_complex_architecture_problem():
    """
    An example function demonstrating how to use the advanced 2026 Self-MoA pipeline.
    """
    print("\n" + "="*60)
    print("🏢 System Architecture Design Assistant (Powered by Self-MoA)")
    print("="*60 + "\n")

    # A complex, multi-faceted prompt that benefits from diverse perspectives
    complex_prompt = """
    I am designing a modern, highly scalable e-commerce platform.
    Requirements:
    1. Must handle 100,000 concurrent users during flash sales.
    2. Needs real-time inventory tracking (preventing overselling).
    3. The frontend is built with Next.js and React.
    4. Database needs to be highly resilient.
    
    Please provide a comprehensive system architecture design including:
    - Recommended backend technologies (language/framework).
    - Database choices (SQL vs NoSQL and why) for the cart vs inventory.
    - Caching strategies.
    - Suggested event-driven messaging systems.
    Provide a specific, actionable justification for each decision.
    """

    # Custom evaluation criteria to guide the aggregator's final synthesis
    strict_criteria = """
    1. Act as a Critical Judge. Analyze the contradictions between the proposed solutions.
    2. The final architecture must favor microservices patterns.
    3. Explicitly recommend exact tools (e.g., Redis, Kafka, PostgreSQL).
    4. Format the response with clear hierarchical Markdown headers and bullet points.
    5. Prioritize high-performance, industry-standard modern solutions.
    """

    print("🧠 Phase 1: Proposing diverse architectural approaches via Temperature Scaling...")
    # Generate 8 diverse drafts distributed between 0.7 and 0.9 temperatures
    drafts = generate_drafts(prompt=complex_prompt, num_drafts=8, temperatures=[0.7, 0.9])
    
    if not drafts:
        print("❌ Failed to generate architectural proposals.")
        return

    print("\n🔍 Phase 2: Single Pass In-Context Reasoning and Synthesis...")
    # Synthesize the drafts at temperature 0 for decisive logic in a single context window
    final_architecture_plan = aggregate_drafts(
        prompt=complex_prompt, 
        drafts=drafts, 
        criteria=strict_criteria
    )

    print("\n" + "*"*30 + " FINAL SYSTEM DESIGN " + "*"*30 + "\n")
    print(final_architecture_plan)
    print("\n" + "*"*81 + "\n")

if __name__ == "__main__":
    solve_complex_architecture_problem()
