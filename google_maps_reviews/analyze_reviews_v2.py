import json
import sys
from pathlib import Path

# Add parent directory to path to allow importing pipeline
BASE_DIR = Path("/Users/karpinski94/projects/google maps scraper/google_maps_reviews")
sys.path.append(str(BASE_DIR.parent))

from pipeline.embedder import embed_texts
from pipeline.clustering import cluster_embeddings
from pipeline.analyzer import analyze_clusters
from pipeline.llm import build_prompt, call_llm
from pipeline.labeler import label_clusters

INPUT_FILE = BASE_DIR / "all_reviews.json"
OUTPUT_JSON = BASE_DIR / "google_analysis_result.json"
OUTPUT_MD = BASE_DIR / "google_analysis_report.md"

MAX_PER_SPLIT = 100 # limit per positive/negative to avoid huge context

def extract_google_reviews(data):
    texts = []
    ratings = []

    for r in data:
        text = (r.get("text") or "").strip()
        rating = r.get("stars") # Google Maps data uses 'stars'

        if text:
            texts.append(text.lower())
            ratings.append(rating)

    return texts, ratings

def split_reviews(texts, ratings):
    positive = []
    negative = []

    for text, rating in zip(texts, ratings):
        if rating is None:
            continue

        if rating >= 4:
            positive.append(text)
        elif rating <= 2:
            negative.append(text)

    return positive, negative

def run_pipeline(texts):
    """Common pipeline flow: embed -> cluster -> analyze -> llm summary"""
    if not texts:
        return [], "No data for this segment."
        
    embeddings = embed_texts(texts)
    labels = cluster_embeddings(embeddings)
    clusters = analyze_clusters(texts, labels)
    
    # LABEL THESE
    print("  Labeling clusters...")
    clusters = label_clusters(clusters)

    prompt = build_prompt(clusters)
    analysis = call_llm(prompt)

    return clusters, analysis

def run_pipeline_on_google(data):
    print("Running pipeline on Google reviews...")

    texts, ratings = extract_google_reviews(data)
    pos, neg = split_reviews(texts, ratings)
    
    # Sampling if too many
    if len(pos) > MAX_PER_SPLIT: pos = pos[:MAX_PER_SPLIT]
    if len(neg) > MAX_PER_SPLIT: neg = neg[:MAX_PER_SPLIT]

    print(f"Positive count: {len(pos)}")
    print(f"Negative count: {len(neg)}")

    # NEGATIVE → pains
    print("\n--- ANALYZING NEGATIVE REVIEWS (PAINS) ---")
    neg_clusters, neg_analysis = run_pipeline(neg)

    # POSITIVE → desires
    print("\n--- ANALYZING POSITIVE REVIEWS (DESIRES) ---")
    pos_clusters, pos_analysis = run_pipeline(pos)

    return {
        "negative_clusters": neg_clusters,
        "negative_analysis": neg_analysis,
        "positive_clusters": pos_clusters,
        "positive_analysis": pos_analysis
    }

def main():
    print("=== Google Maps VoC Analyzer (Clustering Pipeline) ===\n")
    
    if not INPUT_FILE.exists():
        print(f"File not found: {INPUT_FILE}")
        return

    with open(INPUT_FILE, encoding="utf-8") as f:
        data = json.load(f)

    result = run_pipeline_on_google(data)

    # Combine analyses for final report
    final_report = f"""# Google Maps Market Analysis Report

## 🔴 NEGATIVE REVIEWS (PAINS & BARRIERS)
{result['negative']['analysis']}

---

## 🟢 POSITIVE REVIEWS (DESIRES & STRENGTHS)
{result['positive']['analysis']}
"""

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(final_report)
        
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n✅  Clustering saved → {OUTPUT_JSON}")
    print(f"✅  Report saved     → {OUTPUT_MD}")

if __name__ == "__main__":
    main()
