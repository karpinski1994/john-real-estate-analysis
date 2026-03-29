import os
from pipeline.global_analysis import run_analysis_for_source
from pipeline.report_generator import generate_multi_source_report

# Output file
OUTPUT_FILE = "final_market_report.md"

def main():
    print("\n" + "="*40)
    print("🔥 GENERATING MULTI-SOURCE MARKET ANALYSIS...")
    print("="*40 + "\n")

    # 1. Run YouTube Analysis (Market perception, desire)
    print("🎬 STEP 1/2: ANALYZING YOUTUBE DATA...")
    yt_clusters, yt_noise, yt_total = run_analysis_for_source("youtube")
    
    # 2. Run Google Analysis (Customer experience, pain)
    print("\n📍 STEP 2/2: ANALYZING GOOGLE MAPS DATA...")
    google_clusters, google_noise, google_total = run_analysis_for_source("google")

    # 3. Aggregate results
    source_results = {}
    if yt_total > 0:
        source_results['youtube'] = {
            'clusters': yt_clusters,
            'noise_data': yt_noise,
            'total_comments': yt_total
        }
    
    if google_total > 0:
        source_results['google'] = {
            'clusters': google_clusters,
            'noise_data': google_noise,
            'total_comments': google_total
        }

    # 4. Generate Integrated Report
    print("\n📝 6. GENERATING INTEGRATED REPORT...")
    final_report = generate_multi_source_report(source_results)

    # 5. Save report
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(final_report)

    print(f"\n✅ DATA PIPELINE COMPLETE! → saved to {OUTPUT_FILE}")
    print("\nThis report separates Market Perception (YouTube) from Customer Experience (Google).")

if __name__ == "__main__":
    main()
