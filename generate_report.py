from pipeline.query_engine import ask_market
import os

OUTPUT_FILE = "final_market_report.md"

# Specific queries designed to extract a 360-degree view of the market
QUESTIONS = {
    "PAINS": "What are the main frustrations, complaints or negative experiences reported by users?",
    "DESIRES": "What features, services, or outcomes do customers want most or find most attractive?",
    "OBJECTIONS": "What are the common reasons why people hesitate, delay or avoid buying/using these services?",
    "TRUST": "What specific factors create trust or distrust in these real estate companies?",
    "PRICE": "How do people perceive the current pricing? Is it seen as expensive, fair, or a good value?",
    "FEATURES": "What property features or information are most requested in the comments?",
    "UX": "What confuses, frustrates or annoys users about the buying or rental process?",
    "IDENTITY": "What do these customers want to signal about themselves or their status when buying these properties?"
}


def generate_full_report():
    report = "# 🧠 ADVANCED 360° MARKET INTELLIGENCE REPORT\n"
    report += "This report is generated dynamically from 1,500+ real-world VoC data points using an Elite RAG engine.\n\n"

    for section, question in QUESTIONS.items():
        print(f"➡️ Analysing Section: {section}...")

        result = ask_market(question)

        report += f"\n\n# {section}\n\n"
        report += result
        report += "\n\n---\n"

    return report


def main():
    print("\n" + "="*40)
    print("🔥 GENERATING FULL MULTI-SECTION MARKET REPORT...")
    print("="*40 + "\n")

    report = generate_full_report()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n✅ REPORT READY! → Check [final_market_report.md] in your root directory.\n")


if __name__ == "__main__":
    main()
