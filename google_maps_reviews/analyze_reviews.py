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
BASE_DIR   = Path("/Users/karpinski94/projects/google maps scraper")
INPUT_FILE = BASE_DIR / "all_reviews.json"
OUTPUT_MD  = BASE_DIR / "analysis_report.md"
OLLAMA_URL = "http://localhost:11434"

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

MAX_REVIEWS_PER_BATCH = 50  # keep context manageable


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


def reviews_to_text(reviews: list[dict]) -> str:
    """Flatten reviews to a compact text block for the prompt."""
    lines = []
    for r in reviews:
        text = (r.get("text") or r.get("reviewText") or r.get("body") or "").strip()
        rating = r.get("stars") or r.get("rating") or r.get("likert") or ""
        if text:
            lines.append(f"[{rating}★] {text}")
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
    """Pull the first valid JSON object out of the model's response."""
    # strip possible markdown fences
    raw = re.sub(r"```(?:json)?", "", raw).strip()
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
Your task is to thoroughly analyze the provided Google Maps reviews dataset.
Your goal is to produce a comprehensive, deep-dive Voice of Customer (VoC) and behavioral report.

RULES:
1. Provide at least 7-10 distinct insights per category where data allows.
2. Quantify EVERY insight: exact count AND percentage of total reviews.
3. Sort every array in DESCENDING order by percentage.
4. Go deep on psychology: awareness levels, identity, status, fears, desires, JTBD.
5. Quotes MUST be exact, word-for-word snippets from the reviews below.
6. Implications must be sharp, concrete, actionable business/copywriting takeaways.
7. Do NOT generalise — stay specific. List exact names, price points, phrases.
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

---REVIEWS (total dataset: {total} reviews, sample shown below)---
{reviews_text}
---END OF REVIEWS---

Now output the JSON analysis:"""


# =====================
# MARKDOWN RENDERER
# =====================

def render_md(data: dict) -> str:
    lines = ["# Voice of Customer (VoC) — Competitor Reviews Analysis\n"]

    # Distribution
    dist = data.get("distribution", {})
    sent = dist.get("sentiment", {})
    lines += [
        "## 📊 Distribution",
        f"- **Total reviews analysed:** {dist.get('total', 'N/A')}",
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
    print("=== VoC Analyzer ===\n")

    # 1. Load reviews
    print(f"Loading {INPUT_FILE} …")
    with open(INPUT_FILE, encoding="utf-8") as f:
        reviews: list[dict] = json.load(f)
    total = len(reviews)
    print(f"  {total} reviews loaded")

    # 2. Pick model
    model = get_best_model()

    # 3. Build review text (sample if huge)
    sample = reviews[:MAX_REVIEWS_PER_BATCH]
    reviews_text = reviews_to_text(sample)
    print(f"  Using {len(sample)} reviews for analysis prompt")

    # 4. Call LLM
    prompt = build_prompt(reviews_text, total)
    raw_response = call_ollama(model, prompt)

    # 5. Parse JSON
    print("  Parsing response …")
    try:
        analysis = extract_json(raw_response)
    except Exception as e:
        # Save raw for debugging
        raw_path = BASE_DIR / "analysis_raw_response.txt"
        raw_path.write_text(raw_response, encoding="utf-8")
        print(f"  ⚠️  JSON parse failed: {e}")
        print(f"  Raw response saved to {raw_path}")
        sys.exit(1)

    # 6. Save raw JSON too
    json_path = BASE_DIR / "analysis_result.json"
    json_path.write_text(json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Raw JSON saved → {json_path}")

    # 7. Render Markdown
    md = render_md(analysis)
    OUTPUT_MD.write_text(md, encoding="utf-8")
    print(f"\n✅  Report saved → {OUTPUT_MD}")


if __name__ == "__main__":
    main()
