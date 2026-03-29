from database.db import get_conn

def load_all_comments():
    """Load all non-empty comment texts from the database."""
    conn = get_conn()
    cur = conn.cursor()
    
    # Selecting all comments from the comments table
    cur.execute("SELECT text FROM comments")
    rows = cur.fetchall()
    
    conn.close()
    
    # filtering out None or empty strings
    return [r[0] for r in rows if r[0] and r[0].strip()]
