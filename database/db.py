import sqlite3

DB_PATH = "voc.db"

def get_conn():
    """Get a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)


def init_db():
    """Initializes the SQLite database with the prescribed schema."""
    conn = get_conn()
    with open("database/schema.sql") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print(f"✅ Database initialized: {DB_PATH}")

if __name__ == "__main__":
    init_db()
