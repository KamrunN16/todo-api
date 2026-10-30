import os

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv()
DATABASE_URL = os.environ["DATABASE_URL"]


def get_conn():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def init_db():
    conn = get_conn()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT FALSE
            )
            """
        )
        count = conn.execute("SELECT COUNT(*) AS n FROM tasks").fetchone()["n"]
        if count == 0:
            conn.execute("INSERT INTO tasks (title, done) VALUES (%s, %s)", ("Buy groceries", False))
            conn.execute("INSERT INTO tasks (title, done) VALUES (%s, %s)", ("Write report", False))
            conn.execute("INSERT INTO tasks (title, done) VALUES (%s, %s)", ("Call plumber", True))
        conn.commit()
    finally:
        conn.close()