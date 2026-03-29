import httpx
from .config import OLLAMA_URL, LLM_MODEL

def build_prompt(cluster_data):
    """Build a professional McKinsey-level prompt for market research and psychological analysis."""
    text = """
You are a world-class Market Research Analyst, Behavioral Psychologist, and Direct Response Copywriter.

Your task is to analyze REAL user comments grouped into clusters.

You MUST extract deep Voice of Customer insights — similar to professional consulting reports (McKinsey-level).

---

IMPORTANT RULES:

1. Use ONLY the provided quotes (NO hallucination)
2. Each insight MUST include:
   - clear statement
   - % of total comments (use cluster % as proxy)
   - REAL quote
   - implication (VERY IMPORTANT)
3. Be specific — avoid generic statements
4. Think in terms of:
   - fears
   - motivations
   - buying intent
   - objections
5. Group similar patterns into insights

---

DATA:
"""

    for c in cluster_data[:10]:
        name = c.get("name", f"Cluster {c['label']}")
        text += f"\nCluster: {name} ({c['percentage']}% | {c['count']} comments):\n"
        for q in c["quotes"]:
            text += f"- {q}\n"

    text += """

---

OUTPUT STRUCTURE (STRICT):

# 📊 DISTRIBUTION
- Total clusters analyzed
- Key dominant themes (%)

---

# 🧠 PSYCHOLOGICAL DRIVERS

## 🔴 PAINS & FRUSTRATIONS
For each insight:
- Insight title
- % of users
- Quote (REAL)
- Implication (business action)

(min 5 insights)

---

## ✨ DESIRES & MOTIVATIONS
Same structure:
- insight
- %
- quote
- implication

---

## 🏆 STATUS & IDENTITY SIGNALS
What people want to SIGNAL about themselves

---

# 🚧 BARRIERS & OBJECTIONS

## ❌ OBJECTIONS
- what blocks purchase
- include % + quote + implication

## 🔒 TRUST ISSUES
- skepticism, fear, scams

## 💰 PRICE SENSITIVITY
- how users perceive pricing

---

# 🛠 PRODUCT INTELLIGENCE

## 🔧 FEATURE REQUESTS
## 😤 UX COMPLAINTS

---

# 🗣 VOICE OF CUSTOMER

## 🔁 REPEATED PHRASES
## 🪞 IDENTITY STATEMENTS

---

# 🚀 ACTIONABLE INSIGHTS

## 💎 OPPORTUNITIES
## 📣 MESSAGING ANGLES
## 🛡 OBJECTIONS TO ADDRESS

---

FINAL RULES:

- Use bullet points
- Use real quotes
- Include % in every insight
- Be concrete and actionable
- No fluff

"""

    return text

def call_llm(prompt):
    """Call the local LLM via Ollama API."""
    resp = httpx.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": LLM_MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=1200
    )

    resp.raise_for_status()
    data = resp.json()

    if "response" not in data:
        raise ValueError(f"No response from LLM: {data}")

    return data["response"].strip()
