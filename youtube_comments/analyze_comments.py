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
OLLAMA_URL = "http://127.0.0.1:11434"

# Preferred model order (best first). Script picks the first one that's installed.
PREFERRED_MODELS = [
    "llama3.3:70b",
    "llama3.1:70b",
    "qwen2.5:32b",
    "mistral-large",
    "llama3.1:8b",
    "llama3:8b",
    "mistral:7b",
    "qwen2.5:7b",
    "gemma2:9b",
]

MAX_REVIEWS_PER_BATCH = 50  # YouTube comments are shorter, can fit more


# =====================
# HELPERS
# =====================

def get_best_model() -> str:
    resp = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=10)
    resp.raise_for_status()
    installed = {m["name"] for m in resp.json().get("models", [])}
    print(f"Installed models: {installed or '(none)'}")
    for m in PREFERRED_MODELS:
        if m in installed:
            print(f"  → Using: {m}")
            return m
    # fallback: just use whatever is installed
    if installed:
        chosen = sorted(installed)[-1]
        print(f"  → Using fallback: {chosen}")
        return chosen
    sys.exit("❌  No Ollama models installed. Run: docker exec ollama ollama pull llama3.1:8b")


def reviews_to_text(videos: list[dict]) -> str:
    """Flatten nested YouTube comments to a compact text block for the prompt."""
    lines = []
    for v in videos:
        video_title = v.get("video", {}).get("title", "Unknown Video")
        for c in v.get("comments", []):
            text = (c.get("textDisplay") or c.get("textOriginal") or "").strip()
            if text:
                lines.append(f"[Video: {video_title}] {text}")
    return "\n".join(lines)


def call_ollama(model: str, prompt: str) -> str:
    """Stream tokens from Ollama so we print progress live and never hit a read timeout."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        "options": {
            "temperature": 0.2,
            "num_ctx": 16384,
        },
    }
    print("  Streaming from Ollama (tokens will appear below)…", flush=True)
    full_response = []
    with httpx.stream(
        "POST",
        f"{OLLAMA_URL}/api/generate",
        json=payload,
        timeout=httpx.Timeout(connect=15.0, read=None, write=None, pool=None)
    ) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines():
            if not line:
                continue
            chunk = json.loads(line)
            token = chunk.get("response", "")
            print(token, end="", flush=True)
            full_response.append(token)
            if chunk.get("done"):
                break
    print()  # newline after streaming
    return "".join(full_response)


def extract_json(raw: str) -> dict:
    """Pull the first valid JSON object out of the model's response and clean common LLM errors."""
    # strip possible markdown fences
    raw = re.sub(r"```(?:json)?", "", raw).strip()
    
    # Fix common LLM JSON errors:
    # 1. remove unquoted percentages like 2.49% -> 2.49
    raw = re.sub(r"(\"percentage\":\s*)(\d+\.?\d*)%", r"\1\2", raw)
    
    # find outermost {}
    start = raw.find("{")
    if start == -1:
        raise ValueError("No JSON object found in response")
    depth, end = 0, -1
    for i, ch in enumerate(raw[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    return json.loads(raw[start : end + 1])


# =====================
# PROMPT BUILDER
# =====================

SYSTEM_PROMPT = """\
You are a world-class Market Research Analyst, Behavioral Psychologist, and Direct Response Copywriter.
Your task is to thoroughly analyze the provided YouTube comments dataset.
Your goal is to produce a comprehensive, deep-dive Voice of Customer (VoC) and behavioral report.

RULES:
1. Provide at least 7-10 distinct insights per category where data allows.
2. Quantify EVERY insight: exact count AND percentage of total comments.
3. PERCENTAGE MUST BE A NUMBER ONLY. DO NOT ADD THE % SYMBOL (e.g., 2.49, not 2.49%).
4. Sort every array in DESCENDING order by percentage.
5. Go deep on psychology: awareness levels, identity, status, fears, desires, JTBD.
6. Quotes MUST be exact, word-for-word snippets from the comments below.
7. Implications must be sharp, concrete, actionable business/copywriting takeaways.
8. Output ONLY a valid JSON object. No markdown fences, no intro, no outro.

OUTPUT JSON STRUCTURE:
{
  "distribution": {
    "total": number,
    "sentiment": { "positive": number, "neutral": number, "negative": number }
  },
  "psychology": {
    "pains": [{ "text": "string", "count": number, "percentage": number, "quote": "string", "implication": "string" }],
    "failedSolutions": [{ "text": "string", "count": number, "percentage": number, "quote": "string", "implication": "string" }],
    "emotionalCost": [{ "text": "string", "count": number, "percentage": number, "quote": "string", "implication": "string" }],
    "desires": [{ "text": "string", "count": number, "percentage": number, "quote": "string", "implication": "string" }],
    "statusSignals": [{ "text": "string", "count": number, "percentage": number, "quote": "string", "implication": "string" }]
  },
  "barriers": {
    "objections": [{ "text": "string", "count": number, "percentage": number, "quote": "string", "implication": "string" }],
    "trustIssues": [{ "text": "string", "count": number, "percentage": number, "quote": "string", "implication": "string" }],
    "priceSkepticism": [{ "text": "string", "count": number, "percentage": number, "quote": "string", "implication": "string" }],
    "anxietyPatterns": [{ "text": "string", "count": number, "percentage": number, "quote": "string", "implication": "string" }]
  },
  "product": {
    "featureRequests": [{ "text": "string", "count": number, "percentage": number, "quote": "string", "implication": "string" }],
    "uxComplaints": [{ "text": "string", "count": number, "percentage": number, "quote": "string", "implication": "string" }],
    "unintendedUses": [{ "text": "string", "count": number, "percentage": number, "quote": "string", "implication": "string" }]
  },
  "competitors": {
    "directComparisons": [{ "text": "string", "count": number, "percentage": number, "quote": "string", "implication": "string" }],
    "switchingTriggers": [{ "text": "string", "count": number, "percentage": number, "quote": "string", "implication": "string" }]
  },
  "voice": {
    "repeatedPhrases": ["string"],
    "metaphors": ["string"],
    "identityStatements": ["string"]
  },
  "actionable": {
    "opportunities": ["string"],
    "messagingAngles": ["string"],
    "objectionsToAddress": ["string"]
  }
}
"""


def build_prompt(reviews_text: str, total: int) -> str:
    return f"""{SYSTEM_PROMPT}

---COMMENTS (total dataset: {total} comments, sample shown below)---
{reviews_text}
---END OF COMMENTS---

Now output the JSON analysis:"""


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
    print("=== VoC Analyzer (YouTube) ===\n")

    # 1. Load data
    print(f"Loading {INPUT_FILE} …")
    with open(INPUT_FILE, encoding="utf-8") as f:
        videos: list[dict] = json.load(f)
    
    # Count total comments for accurate stats
    total_comments = sum(len(v.get("comments", [])) for v in videos)
    print(f"  {len(videos)} videos with total {total_comments} comments loaded")

    # 2. Pick model
    model = get_best_model()

    # 3. Build text (limit videos if too many, currently 100 max comments)
    # We take comments until we reach roughly MAX_REVIEWS_PER_BATCH
    sample_videos = []
    current_count = 0
    for v in videos:
        count = len(v.get("comments", []))
        if count == 0: continue
        sample_videos.append(v)
        current_count += count
        if current_count >= MAX_REVIEWS_PER_BATCH:
            break

    reviews_text = reviews_to_text(sample_videos)
    print(f"  Using {current_count} comments for analysis prompt")

    # 4. Call LLM
    prompt = build_prompt(reviews_text, total_comments)
    raw_response = call_ollama(model, prompt)

    # 5. Parse JSON
    print("  Parsing response …")
    try:
        analysis = extract_json(raw_response)
    except Exception as e:
        # Save raw for debugging
        raw_path = BASE_DIR / "analysis_raw_response_yt.txt"
        raw_path.write_text(raw_response, encoding="utf-8")
        print(f"  ⚠️  JSON parse failed: {e}")
        print(f"  Raw response saved to {raw_path}")
        sys.exit(1)

    # 6. Save raw JSON too
    json_path = BASE_DIR / "youtube_analysis_result.json"
    json_path.write_text(json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Raw JSON saved → {json_path}")

    # 7. Render Markdown
    md = render_md(analysis)
    OUTPUT_MD.write_text(md, encoding="utf-8")
    print(f"\n✅  Report saved → {OUTPUT_MD}")


if __name__ == "__main__":
    main()

