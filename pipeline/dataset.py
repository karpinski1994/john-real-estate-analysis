from database.db import get_conn

def load_all_comments():
    """Load all text comments from the database."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT text FROM comments")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows if row[0]]

def load_comments_by_source(source: str):
    """
    Load comments filtered by source.
    source can be: 'youtube' or 'google'
    """
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT text FROM comments WHERE source = ?", (source,))
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows if row[0]]
