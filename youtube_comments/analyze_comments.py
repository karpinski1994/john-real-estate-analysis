#!/usr/bin/env python3
"""
VoC Analyzer — reads all_reviews.json, picks the best available Ollama model,
runs deep market-research analysis, and saves the result as analysis_report.md
"""

import json
import re
import sys
import textwrap
from pathlib import Path

import httpx

# =====================
# CONFIG
# =====================
BASE_DIR   = Path("/Users/karpinski94/projects/google maps scraper/youtube_comments")
INPUT_FILE = BASE_DIR / "apartamentos-en-venta-medellin.json"
OUTPUT_MD  = BASE_DIR / "youtube_analysis_report.md"
OUTPUT_JSON = BASE_DIR / "youtube_analysis_result.json"

# Add parent directory to path to allow importing pipeline
import sys
sys.path.append(str(BASE_DIR.parent))

from pipeline.embedder import embed_texts
from pipeline.clustering import cluster_embeddings
from pipeline.analyzer import analyze_clusters
from pipeline.llm import build_prompt, call_llm
from pipeline.preprocessing import clean_text
from pipeline.labeler import label_clusters
from pipeline.aggregator import merge_clusters, group_by_theme
from pipeline.report import generate_report

# IMPORT GOOGLE RUNNER
import sys
GOOGLE_DIR = Path("/Users/karpinski94/projects/google maps scraper/google_maps_reviews")
sys.path.append(str(GOOGLE_DIR))
import analyze_reviews_v2 as google_pipeline

MAX_REVIEWS_PER_BATCH = 250


# =====================
# PROCESSING
# =====================

def extract_youtube_texts(videos):
    """Extract and clean comments from YouTube data structure."""
    texts = []
    for v in videos:
        for c in v.get("comments", []):
            text = (c.get("textDisplay") or c.get("textOriginal") or "").strip()
            # USE CLEANER
            clean = clean_text(text)
            if clean:
                texts.append(clean)
    return texts


def run_pipeline_on_youtube(videos):
    """Orchestrate the AI pipeline for YouTube comments."""
    print("Running pipeline on YouTube comments...")

    # 1. Preprocessing
    texts = extract_youtube_texts(videos)
    # Limiting to manage context size if needed
    if len(texts) > MAX_REVIEWS_PER_BATCH:
        print(f"  Truncating {len(texts)} comments to {MAX_REVIEWS_PER_BATCH}...")
        texts = texts[:MAX_REVIEWS_PER_BATCH]

    print(f"Total comments to analyze: {len(texts)}")

    # 2. AI Pipeline
    embeddings = embed_texts(texts)
    labels = cluster_embeddings(embeddings)
    clusters = analyze_clusters(texts, labels)
    
    # 3. Labeling
    print("Labeling clusters...")
    clusters = label_clusters(clusters)

    # 4. LLM Final Result
    prompt = build_prompt(clusters)
    analysis = call_llm(prompt)

    return clusters, analysis


# =====================
# MARKDOWN RENDERER
# =====================

def render_md(data: dict) -> str:
    lines = ["# Voice of Customer (VoC) — YouTube Comments Analysis\n"]

    # Distribution
    dist = data.get("distribution", {})
    sent = dist.get("sentiment", {})
    lines += [
        "## 📊 Distribution",
        f"- **Total comments analysed:** {dist.get('total', 'N/A')}",
        f"- 🟢 Positive: {sent.get('positive', 'N/A')}",
        f"- 🟡 Neutral: {sent.get('neutral', 'N/A')}",
        f"- 🔴 Negative: {sent.get('negative', 'N/A')}",
        "",
    ]

    def render_section(title: str, items: list, emoji: str = "•"):
        if not items:
            return
        lines.append(f"### {emoji} {title}")
        for i in items:
            lines.append(
                f"- **{i.get('text', '')}** — `{i.get('count', '?')} mentions ({i.get('percentage', '?')}%)`"
            )
            q = i.get("quote", "")
            if q:
                lines.append(f'  > *"{q}"*')
            impl = i.get("implication", "")
            if impl:
                lines.append(f"  💡 {impl}")
        lines.append("")

    # Psychology
    psy = data.get("psychology", {})
    lines.append("## 🧠 Psychology\n")
    render_section("Pains", psy.get("pains", []), "😣")
    render_section("Failed Solutions", psy.get("failedSolutions", []), "❌")
    render_section("Emotional Cost", psy.get("emotionalCost", []), "💔")
    render_section("Desires", psy.get("desires", []), "✨")
    render_section("Status Signals", psy.get("statusSignals", []), "🏆")

    # Barriers
    bar = data.get("barriers", {})
    lines.append("## 🚧 Barriers\n")
    render_section("Objections", bar.get("objections", []), "🙅")
    render_section("Trust Issues", bar.get("trustIssues", []), "🔒")
    render_section("Price Skepticism", bar.get("priceSkepticism", []), "💰")
    render_section("Anxiety Patterns", bar.get("anxietyPatterns", []), "😰")

    # Product
    prod = data.get("product", {})
    lines.append("## 🛠️ Product Insights\n")
    render_section("Feature Requests", prod.get("featureRequests", []), "🔧")
    render_section("UX Complaints", prod.get("uxComplaints", []), "😤")
    render_section("Unintended Uses", prod.get("unintendedUses", []), "🔀")

    # Competitors
    comp = data.get("competitors", {})
    lines.append("## ⚔️ Competitors\n")
    render_section("Direct Comparisons", comp.get("directComparisons", []), "🆚")
    render_section("Switching Triggers", comp.get("switchingTriggers", []), "🔄")

    # Voice
    voice = data.get("voice", {})
    lines.append("## 🗣️ Voice of Customer\n")
    if voice.get("repeatedPhrases"):
        lines.append("### 🔁 Repeated Phrases")
        for p in voice["repeatedPhrases"]:
            lines.append(f'- *"{p}"*')
        lines.append("")
    if voice.get("metaphors"):
        lines.append("### 🖼️ Metaphors & Imagery")
        for m in voice["metaphors"]:
            lines.append(f"- {m}")
        lines.append("")
    if voice.get("identityStatements"):
        lines.append("### 🪞 Identity Statements")
        for s in voice["identityStatements"]:
            lines.append(f"- {s}")
        lines.append("")

    # Actionable
    act = data.get("actionable", {})
    lines.append("## 🚀 Actionable Takeaways\n")
    if act.get("opportunities"):
        lines.append("### 💎 Opportunities")
        for o in act["opportunities"]:
            lines.append(f"- {o}")
        lines.append("")
    if act.get("messagingAngles"):
        lines.append("### 📣 Messaging Angles")
        for a in act["messagingAngles"]:
            lines.append(f"- {a}")
        lines.append("")
    if act.get("objectionsToAddress"):
        lines.append("### 🛡️ Objections to Address")
        for o in act["objectionsToAddress"]:
            lines.append(f"- {o}")
        lines.append("")

    return "\n".join(lines)


# =====================
# MAIN
# =====================

def main():
    print("=== Combined VoC Insight Engine (YouTube + Google) ===\n")
    
    # --- 1. YOUTUBE PIPELINE ---
    if not INPUT_FILE.exists():
        print(f"File not found: {INPUT_FILE}")
        return

    with open(INPUT_FILE, encoding="utf-8") as f:
        videos = json.load(f)

    # Note: run_pipeline_on_youtube handles its own printing
    yt_clusters, yt_analysis = run_pipeline_on_youtube(videos)


    # --- 2. GOOGLE PIPELINE ---
    print("\n\n=== RUNNING GOOGLE MAPS SEGMENTED ANALYSIS ===")
    G_INPUT = GOOGLE_DIR / "all_reviews.json"
    if G_INPUT.exists():
        with open(G_INPUT, encoding="utf-8") as f:
            g_data = json.load(f)
        
        # Triggering the Google's full analysis logic
        g_results = google_pipeline.run_pipeline_on_google(g_data)
        
        g_pos = g_results.get("positive_clusters", [])
        g_neg = g_results.get("negative_clusters", [])
    else:
        print(f"Google data not found at {G_INPUT}")
        g_pos, g_neg = [], []


    # --- 3. MERGE & AGGREGATE ---
    print("\n--- Aggregating Market Themes ---")
    merged = merge_clusters(yt_clusters, g_pos, g_neg)
    grouped = group_by_theme(merged)


    # --- 4. GENERATE REPORT ---    
    final_report = generate_report(grouped)
    
    REPORT_PATH = BASE_DIR / "combined_voc_report.md"
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(final_report)

    # Final Output
    print("\n" + "="*40)
    print("👑 UNIFIED MARKET INSIGHTS")
    print("="*40)
    print(final_report)
    print(f"\n✅ Final Market Report saved to: {REPORT_PATH}")
    print("="*40)


if __name__ == "__main__":
    main()
