from pipeline.embedder import embed_texts
from pipeline.vector_store import VectorStore
from pipeline.storage import get_comment_by_id


def rerank_results(results):
    """Filters noise and deduplicates comments for higher analytical quality."""
    # Filter by length (too short are usually just noise, too long are outliers)
    results = [r for r in results if 10 < len(r) < 500]
    
    # Deduplication using a set
    seen = set()
    cleaned = []
    for r in results:
        if r not in seen:
            cleaned.append(r)
            seen.add(r)
            
    return cleaned[:20]  # Return top 20 high-quality candidates


def search_similar(query, k=50):
    """Performs a hybrid search combining FAISS semantic vectors with keyword relevance boosting."""
    # Note: nomic-embed-text has a dimension of 768
    store = VectorStore(dim=768)
    
    try:
        store.load()
    except Exception as e:
        print(f"Error loading index: {e}. Build it first!")
        return []

    # 1. Semantic Search (Broad)
    q_emb = embed_texts([query])[0]
    ids = store.search(q_emb, k=k)

    semantic_results = []
    for cid in ids:
        text = get_comment_by_id(cid)
        if text:
            semantic_results.append(text)

    # 2. Keyword Relevance Boosting
    keywords = query.lower().split()
    
    scored_results = []
    for text in semantic_results:
        # Score based on keyword overlap
        score = sum(1 for kw in keywords if kw in text.lower())
        scored_results.append((score, text))

    # Sort by keyword relevance first, then semantic position
    scored_results.sort(key=lambda x: x[0], reverse=True)
    
    # 3. Rerank & Prune
    final_results = [text for score, text in scored_results]
    return rerank_results(final_results)
