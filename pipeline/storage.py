import json
from database.db import get_conn


def save_comment_with_embedding(text, embedding, source="unknown"):
    """Persists a comment and its corresponding embedding vector in the SQLite database."""
    conn = get_conn()
    cur = conn.cursor()

    # insert comment
    cur.execute(
        "INSERT OR IGNORE INTO comments (text, source) VALUES (?, ?)",
        (text, source)
    )
    conn.commit()

    # get id
    cur.execute("SELECT id FROM comments WHERE text = ?", (text,))
    res = cur.fetchone()
    if not res:
        conn.close()
        return None
        
    comment_id = res[0]

    # insert embedding
    vector_json = json.dumps(embedding.tolist() if hasattr(embedding, "tolist") else list(embedding))
    cur.execute(
        "INSERT OR IGNORE INTO embeddings (comment_id, vector) VALUES (?, ?)",
        (comment_id, vector_json)
    )

    conn.commit()
    conn.close()

    return comment_id


def get_comment_by_id(comment_id):
    """Retrieves the raw text of a comment by its database ID."""
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT text FROM comments WHERE id = ?", (comment_id,))
    row = cur.fetchone()

    conn.close()

    return row[0] if row else None
