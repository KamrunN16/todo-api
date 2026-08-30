import sqlite3

DB_PATH = "tasks.db"


def get_conn():
    """Open (and implicitly create, if missing) the SQLite database file."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Enforce foreign keys / sane defaults; not strictly needed for one table,
    # but good habit for a real project.
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create the tasks table if it doesn't exist, and seed 3 example tasks
    the very first time (only if the table is currently empty)."""
    conn = get_conn()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT 0
            )
            """
        )

        (count,) = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()
        if count == 0:
            # Wrapped implicitly in a transaction: sqlite3's default
            # isolation level means these three inserts commit together.
            conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Buy groceries", 0))
            conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Write report", 0))
            conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Call plumber", 1))
            conn.commit()
    finally:
        conn.close()
