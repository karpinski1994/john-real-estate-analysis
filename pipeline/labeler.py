import httpx
import time
from .config import OLLAMA_URL, LLM_MODEL

def label_clusters(cluster_data):
    """
    Use the LLM to name clusters based on representative quotes.
    Optimized for stability: 
    - Limits to top 30 clusters
    - Increased timeout
    - Sleep between requests
    - Strict formatting
    """
    labeled = []

    for i, c in enumerate(cluster_data):
        # 🔥 STEP 1: LIMIT TO TOP 30 (Value focus)
        if i >= 30:
            c["name"] = f"Other Feedback {i}"
            labeled.append(c)
            continue

        quotes = "\n".join(c["quotes"])

        # 🔥 STEP 2: STRICT PROMPT (Copy-Paste from Requirements)
        prompt = f"""
        You are a strict data labeling system.

        Your ONLY task is to assign a short, precise label to a group of similar user comments.

        ---

        INPUT:
        A group of real user comments that are already clustered by similarity.

        ---

        RULES:

        1. DO NOT analyze, explain, or summarize.
        2. DO NOT generate insights, reports, or strategies.
        3. DO NOT invent percentages or statistics.
        4. DO NOT add any extra text.

        5. Your job is ONLY:
           → Identify what these comments have in common
           → Name that theme in 2-4 words MAX

        6. The label MUST:
           - Be specific (NOT generic like "Feedback" or "Comments")
           - Be concrete (e.g. "High Prices", "No Pool", "Bad Kitchen Design")
           - Reflect actual user language

        7. Language:
           - Output in English
           - Use simple, clear wording

        ---

        EXAMPLES:

        Comments:
        - "too expensive"
        - "price is too high"
        - "very costly apartments"

        Output:
        High Prices


        Comments:
        - "no swimming pool"
        - "there is no pool"
        - "missing pool in building"

        Output:
        No Pool


        Comments:
        - "kitchen looks bad"
        - "i don't like the kitchen"
        - "kitchen design is terrible"

        Output:
        Bad Kitchen Design

        ---

        NOW LABEL THIS CLUSTER:

        {quotes}

        ---

        OUTPUT:
        (ONLY the label, nothing else)
        """

        try:
            # 🔥 STEP 3: HIGH TIMEOUT + OLLAMA CALL
            resp = httpx.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": LLM_MODEL,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=120
            )

            resp.raise_for_status()
            name = resp.json()["response"].strip()
            
            # 💡 CLEANUP
            name = name.strip('"').strip("'").strip().split('\n')[0] # Get only first line in case of hallucinations
            
            # 🔥 FALLBACK: Ensure the label is short
            if len(name.split()) > 5:
                name = " ".join(name.split()[:3])

            c["name"] = name
            
            # 💤 STEP 4: RATE LIMITING (Don't spam Ollama)
            time.sleep(0.5)

        except Exception as e:
            print(f"⚠️ Error labeling cluster: {e}")
            c["name"] = "General Issue"
            
        labeled.append(c)

    return labeled
