from pipeline.embedder import embed_texts
from pipeline.storage import save_comment_with_embedding
from pipeline.vector_store import VectorStore


def build_index(texts):
    """Embed, persist, and index a list of market comments for semantic search."""
    if not texts:
        print("Empty text list, skipping index build.")
        return
        
    embeddings = embed_texts(texts)

    # Initialize VectorStore with embedding dimension
    store = VectorStore(dim=len(embeddings[0]))

    ids = []

    for text, emb in zip(texts, embeddings):
        # Save to SQLite and get the persistent comment_id
        comment_id = save_comment_with_embedding(text, emb)
        if comment_id:
            ids.append(comment_id)

    # Add to FAISS and save index
    store.add(embeddings, ids)
    store.save()

    print(f"✅ Index built with {len(ids)} comments and saved to faiss.index")
