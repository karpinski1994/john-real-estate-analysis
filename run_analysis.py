import json
import random
from pathlib import Path
from youtube_comments.analyze_comments import extract_youtube_texts

from pipeline.embedder import embed_texts
from pipeline.clustering import cluster_embeddings
from pipeline.analyzer import analyze_clusters
from pipeline.labeler import label_clusters
from pipeline.llm import build_prompt, call_llm


def run_pipeline(texts):
    """Run the full AI pipeline on a list of cleaned texts."""
    if not texts:
        return "No data for analysis."

    # 1. Embed & Cluster
    embeddings = embed_texts(texts)
    labels = cluster_embeddings(embeddings)
    
    # 2. Analyze & Label
    clusters = analyze_clusters(texts, labels)
    clusters = label_clusters(clusters)

    # 3. LLM Deep Insight
    prompt = build_prompt(clusters)
    analysis = call_llm(prompt)

    return analysis


def main():
    print("🔥 Starting Minimal VoC Insight Engine...\n")

    # ========= YOUTUBE =========
    YT_FILE = "youtube_comments/apartamentos-en-venta-medellin.json"
    if Path(YT_FILE).exists():
        with open(YT_FILE, encoding="utf-8") as f:
            yt_data = json.load(f)

        yt_texts = extract_youtube_texts(yt_data)
        print(f"Loaded {len(yt_texts)} YouTube comments. Analyzing top 150...")
        
        yt_analysis = run_pipeline(yt_texts[:150])

        print("\n\n" + "="*20)
        print("📊 YOUTUBE MARKET INSIGHTS")
        print("="*20 + "\n")
        print(yt_analysis)
    else:
        print(f"Skipping YouTube: {YT_FILE} not found.")


    # ========= GOOGLE =========
    GOOGLE_FILE = "google_maps_reviews/all_reviews.json"
    if Path(GOOGLE_FILE).exists():
        print("\n\n" + "="*40)
        print("🔥 GOOGLE MAPS ANALYSIS")
        print("="*40 + "\n")
        
        with open(GOOGLE_FILE, encoding="utf-8") as f:
            google_data = json.load(f)

        # Basic extraction for minimal runner
        texts = []
        for r in google_data:
            text = (r.get("text") or "").strip()
            if text:
                texts.append(text.lower())
        
        print(f"Loaded {len(texts)} Google reviews. Analyzing top 150...")
        google_analysis = run_pipeline(texts[:150])

        print("\n\n" + "="*20)
        print("📊 GOOGLE MAPS MARKET INSIGHTS")
        print("="*20 + "\n")
        print(google_analysis)
        
        # --- SAVE FINAL COMBINED DEEP REPORT ---
        full_report = f"""# 🔥 FINAL VoC DEEP MARKET REPORT

This report combines deep psychological analysis from YouTube and Google Maps.

## 🎥 YOUTUBE DEEP ANALYSIS
{yt_analysis}

---

## 🗺 GOOGLE MAPS DEEP ANALYSIS
{google_analysis}

---
*Report generated via AI Insight Engine*
"""

        FINAL_REPORT_PATH = "final_voc_report.md"
        with open(FINAL_REPORT_PATH, "w", encoding="utf-8") as f:
            f.write(full_report)

        print("\n" + "="*40)
        print(f"✅ FINAL CONSULTING REPORT saved → {FINAL_REPORT_PATH}")
        print("="*40 + "\n")
    else:
        print(f"Skipping Google: {GOOGLE_FILE} not found.")


if __name__ == "__main__":
    main()
