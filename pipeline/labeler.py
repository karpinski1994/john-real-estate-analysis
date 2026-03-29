import httpx
from .config import OLLAMA_URL, LLM_MODEL

def label_clusters(cluster_data):
    """Use the LLM to name clusters based on representative quotes."""
    labeled = []

    for c in cluster_data[:10]:
        quotes = "\n".join(c["quotes"])

        prompt = f"""
Name this cluster based on user quotes:

{quotes}

Rules:
- Max 3 words.
- Specific and descriptive.
- No generic words like "comments" or "feedback".
- Return the label in English.

Only return the label.
"""

        resp = httpx.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": LLM_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        resp.raise_for_status()
        name = resp.json()["response"].strip()

        c["name"] = name
        labeled.append(c)

    return labeled
