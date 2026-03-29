import httpx
import numpy as np
from tqdm import tqdm
from .config import OLLAMA_URL, EMBED_MODEL


def embed_texts(texts):
    embeddings = []

    for text in tqdm(texts, desc="Embedding"):
        resp = httpx.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={
                "model": EMBED_MODEL,
                "prompt": text
            },
            timeout=30
        )

        resp.raise_for_status()

        data = resp.json()

        if "embedding" not in data:
            raise ValueError(f"No embedding returned: {data}")

        embeddings.append(data["embedding"])

    return np.array(embeddings)
