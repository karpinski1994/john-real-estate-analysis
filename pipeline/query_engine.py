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
    """Elite Query Engine: Intent detection, insight density counting, and RAG synthesis."""
    print(f"🕵️  Elite Market Analysis for inquiry: '{question}'...")
    
    # 1. Intent Detection
    intent = detect_intent(question)
    
    # 2. Hybrid Search
    results = search_similar(question, k=50)
    
    # 3. Frequency & Density Guards
    if not results:
        return "INSUFFICIENT DATA: No relevant market evidence found."
    
    density_rank = "HIGH" if len(results) >= 20 else "MEDIUM"
    if len(results) < 10:
        density_rank = "LOW (Caution: Sparse data)"

    # 4. Pattern Counting & Grouping
    pattern_freq = count_patterns(results)
    context = group_similar(results)

    # 5. Elite Prompting
    prompt = f"""
You are a Lead Strategic Consultant and Behavioral Psychologist.

Your task is to analyze the provided market data. 
You are performing a: **{intent}** analysis.

---
INSIGHT DENSITY (PATTERN FREQUENCY):
{pattern_freq}
---
RAW DATA (CONTEXT):
{context}
---

STRICT ANALYTICAL RULES:
1. FOCUS: Pay special attention to the {intent} aspect of the data.
2. WEIGHTING: Repeated patterns (Insight Density) are more important than outliers.
3. GROUNDING: Every claim MUST be backed by a direct quote below it.
4. CONFIDENCE: Ensure your confidence level matches the source density (Rank: {density_rank}).
5. HONESTY: If the data is contradictory or thin, explicitly state the limitations.

OUTPUT FORMAT:

# 📊 MARKET INTELLIGENCE REPORT

## 🎯 CORE PATTERN: {intent}
- Summarize the dominant market sentiment in 2 sentences.

## 💡 KEY BEHAVIORAL INSIGHTS
- Insight Statement (Highlight the % frequency/density derived from counts)
- REAL QUOTE Evidence

## 📈 STRATEGIC IMPLICATIONS & ACTION PLAN
- Exactly what the brand should do to exploit this opportunity or mitigate this risk.

## 🚥 DATA CONFIDENCE: {density_rank}
- Justify this based on the number of data points and repeats found.
"""

    return call_llm(prompt)
