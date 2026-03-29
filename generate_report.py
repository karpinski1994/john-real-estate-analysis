from pipeline.query_engine import ask_market
from pipeline.llm import call_llm
import os

OUTPUT_FILE = "final_market_report.md"

# Strategic queries for a comprehensive 360-degree audit
QUESTIONS = {
    "PAINS": "What are the main frustrations, complaints or specific negative behaviors reported?",
    "DESIRES": "What specific outcomes, luxury features or states of being do customers desire most?",
    "OBJECTIONS": "What specifically makes people hesitate, doubt, or delay their purchase decisions?",
    "TRUST": "What specific company actions or behaviors create trust or destroy credibility?",
    "PRICE": "How specifically do people react to prices? Is there a disconnect between price and value?",
    "TENSIONS": "Identify conflicting market signals (e.g. people love the design but hate the service/location).",
    "UX": "What concrete steps in the buying or interaction process confuse or annoy users?",
    "STRATEGY": "Based on all of the above, what is the single biggest opportunity for growth?"
}


def refine_report(full_text):
    """Performs a global 'Meta-Pass' to ensure consistency, remove contradictions, and align tone."""
    print("\n🧐 Refinement Pass: Aligning insights and removing inconsistencies...")
    
    prompt = f"""
You are a Lead Strategic Consultant (McKinsey/BCG level). 

Your task is to refine and edit the following market research report.

STRICT INSTRUCTIONS:
1. REMOVE CONTRADICTIONS: Ensure PAINS do not contradict DESIRES.
2. REMOVE CONTRIVED %: If you see any % that look hallucinated vs exact counts, replace them with accurate relative terms (e.g., "Dominant Theme", "Frequent Signal").
3. ENFORCE SPECIFICITY: Replace generic advice with concrete strategic actions.
4. ALIGN TONE: Ensure the report flows as a cohesive narrative.
5. HIGHLIGHT TENSIONS: Ensure the tension between opposing market forces is clear.

REPORT TO REFINE:
{full_text}
"""
    return call_llm(prompt)


def generate_full_report():
    report = "# 🧠 ELITE 360° MARKET AUDIT: MEDELLIN REAL ESTATE\n"
    report += "This strategic audit synthesizes over 1,500 real-world data points into actionable market intelligence.\n\n"

    for section, question in QUESTIONS.items():
        print(f"➡️ Analysing: {section}...")

        result = ask_market(question)

        report += f"\n# {section}\n\n"
        report += result
        report += "\n\n---\n"

    return report


def main():
    print("\n" + "="*40)
    print("🔥 GENERATING ELITE MARKET AUDIT...")
    print("="*40 + "\n")

    # Step 1: Raw Generation
    raw_report = generate_full_report()
    
    # Step 2: Global Refinement (Meta-Pass)
    final_report = refine_report(raw_report)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(final_report)

    print(f"\n✅ ELITE AUDIT COMPLETE! → saved to {OUTPUT_FILE}\n")


if __name__ == "__main__":
    main()
