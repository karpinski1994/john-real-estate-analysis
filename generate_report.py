from pipeline.global_analysis import run_global_analysis
from pipeline.report_generator import generate_structured_report
import os

OUTPUT_FILE = "final_market_report.md"

def main():
    print("\n" + "="*40)
    print("🔥 GENERATING STRUCTURED MARKET ANALYSIS...")
    print("="*40 + "\n")

    # Step 1: Run Global Data Analysis (Loading, Embedding, Clustering, Naming)
    # This replaces the previous RAG/query_engine approach
    clusters, total_comments = run_global_analysis()
    
    if not clusters:
        print("❌ Report generation aborted: No clusters identified.")
        return

    # Step 2: Generate the report using pure Python logic (no LLM here)
    # This prevents hallucinated percentages and strategies.
    print("\n📝 6. GENERATING FINAL REPORT (PURE PYTHON)...")
    final_report = generate_structured_report(clusters, total_comments)

    # Step 3: Save the final report
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(final_report)

    print(f"\n✅ DATA PIPELINE COMPLETE! → saved to {OUTPUT_FILE}\n")
    print("This report is strictly based on cluster-counts and real user quotes.")


if __name__ == "__main__":
    main()
