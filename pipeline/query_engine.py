from collections import defaultdict, Counter
from pipeline.search import search_similar
from pipeline.llm import call_llm


def detect_intent(query):
    """Classifies the psychological category of the user's market inquiry."""
    q = query.lower()
    if any(w in q for w in ["why", "problem", "bad", "negative", "issue", "fail"]):
        return "PAIN / FRICTION"
    if any(w in q for w in ["want", "like", "best", "good", "luxury", "desire"]):
        return "DESIRE / MOTIVATION"
    if any(w in q for w in ["afraid", "scam", "trust", "hesitate", "risk", "fake"]):
        return "OBJECTION / BARRIER"
    if any(w in q for w in ["compare", "vs", "better", "different"]):
        return "COMPARISON / POSITIONING"
    return "GENERAL MARKET OVERVIEW"


def count_patterns(results):
    """Calculates frequency of similar perspectives to determine pattern weight."""
    # Group by first 40 chars to find near-duplicates or highly similar phrases
    short_patterns = [r[:40].lower().strip() for r in results]
    counts = Counter(short_patterns)
    
    # Return a formatted string for the LLM
    top_patterns = "\n".join([f"- '{pat}...' cited {count} times" for pat, count in counts.most_common(10)])
    return top_patterns


def group_similar(results):
    """Groups similar comments to help the LLM identify frequency and weight."""
    groups = defaultdict(list)
    for r in results:
        key = r[:25].lower()
        groups[key].append(r)
    
    context = ""
    for _, items in groups.items():
        if len(items) > 1:
            context += f"\n[PATTERN REPETITION - {len(items)} Occurrences]:\n"
        context += "\n".join([f"- {it}" for it in items]) + "\n"
    
    return context


def ask_market(question):
    """Elite Query Engine: Data-driven synthesis with strict grounding and intent recognition."""
    print(f"🕵️  Analysing Inquiry: '{question}'...")
    
    # 1. Intent & Hybrid Search
    intent = detect_intent(question)
    results = search_similar(question, k=50)
    
    if not results:
        return "INSUFFICIENT DATA: No relevant market evidence found."
    
    # 2. Density & Pattern Weighting
    density_rank = "HIGH" if len(results) >= 20 else "MEDIUM"
    if len(results) < 10:
        density_rank = "LOW"

    pattern_freq = count_patterns(results)
    context = group_similar(results)

    # 3. Targeted Senior Analyst Prompt
    prompt = f"""
You are a Senior Strategic Market Analyst. 

Your task is to analyze the provided market data for the core intent: **{intent}**.

STRICT RULES:
1. USE ONLY PROVIDED DATA: If something isn't in the comments, it doesn't exist.
2. NO HALLUCINATED %: Do NOT invent percentages (e.g., "40% said...").
3. RELATIVE FREQUENCY: Use terms like "High Signal", "Moderately Frequent", or "Isolated Mention" based on data density.
4. BE SPECIFIC: Avoid generic statements like "customers want good service." Be concrete (e.g., "Users express frustration over WhatsApp response delays").
5. EVERY INSIGHT MUST HAVE A QUOTE: Link every behavioral claim to a supporting quote from the context.
6. FOCUS ON BEHAVIORS: Analyze what users ACTUALLY DO (actions, complaints, specific requests) rather than general opinions.

User question: 
"{question}"

---
CONTEXT (Pattern Frequency & Quotes):
{pattern_freq}
{context}
---

OUTPUT FORMAT (No extra headers):

### 🎯 CORE PATTERN
- 1-2 sentences on the dominant behavioral theme discovered.

### 💡 KEY BEHAVIORAL INSIGHTS
- Specific Insight (Relative Frequency: High/Med/Low)
- REAL QUOTE Example

### 🔍 EVIDENCE
- Provide 3-5 additional supportive quotes.

### 📈 STRATEGIC IMPLICATIONS
- Concrete business action or marketing adjustment based on this specific data.

### 🚥 CONFIDENCE: {density_rank}
- Brief justification of why this rank was chosen.
"""

    return call_llm(prompt)
