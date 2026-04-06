import contextlib
import json
import os

import psycopg2
import psycopg2.extras
from psycopg2.pool import ThreadedConnectionPool

DATABASE_URL = os.getenv("DATABASE_URL")

_pool: ThreadedConnectionPool | None = None


def _get_pool() -> ThreadedConnectionPool:
    global _pool
    if _pool is None:
        _pool = ThreadedConnectionPool(minconn=2, maxconn=10, dsn=DATABASE_URL)
    return _pool


@contextlib.contextmanager
def get_conn():
    pool = _get_pool()
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)


def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id             TEXT PRIMARY KEY,
                    title          TEXT NOT NULL,
                    messages       JSONB NOT NULL DEFAULT '[]',
                    documents      JSONB NOT NULL DEFAULT '[]',
                    selected_model TEXT NOT NULL DEFAULT 'llama-3.3-70b-versatile',
                    vectorization_status   TEXT DEFAULT 'idle',
                    vectorization_progress INTEGER DEFAULT 0,
                    created_at     TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            # Guard for existing deployments that may lack these columns
            cur.execute("ALTER TABLE sessions ADD COLUMN IF NOT EXISTS vectorization_status TEXT DEFAULT 'idle'")
            cur.execute("ALTER TABLE sessions ADD COLUMN IF NOT EXISTS vectorization_progress INTEGER DEFAULT 0")
        conn.commit()


def list_sessions():
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM sessions ORDER BY created_at ASC")
            return [_row_to_dict(r) for r in cur.fetchall()]


def get_session(id: str):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM sessions WHERE id = %s", (id,))
            row = cur.fetchone()
            return _row_to_dict(row) if row else None


def create_session(id: str, title: str, selected_model: str = "llama-3.3-70b-versatile"):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO sessions (id, title, selected_model) VALUES (%s, %s, %s)",
                (id, title, selected_model),
            )
        conn.commit()


def update_session(id: str, **kwargs):
    """Update any combination of: messages, documents, title, selected_model."""
    allowed = {"messages", "documents", "title", "selected_model"}
    fields = {
        k: (json.dumps(v) if isinstance(v, list) else v)
        for k, v in kwargs.items()
        if k in allowed
    }
    if not fields:
        return
    sets = ", ".join(f"{k} = %s" for k in fields)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE sessions SET {sets} WHERE id = %s",
                [*fields.values(), id],
            )
        conn.commit()


def update_vectorization_progress(id: str, status: str, progress: int):
    print(f"DEBUG: Updating DB for session {id} -> status: {status}, prog: {progress}")
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE sessions SET vectorization_status = %s, vectorization_progress = %s WHERE id = %s",
                (status, progress, id),
            )
        conn.commit()


def delete_session(id: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM sessions WHERE id = %s", (id,))
        conn.commit()


def _row_to_dict(row):
    d = dict(row)
    d["selectedModel"] = d.pop("selected_model")
    d["vectorizationStatus"] = d.pop("vectorization_status") or "idle"
    d["vectorizationProgress"] = d.pop("vectorization_progress") or 0
    if not isinstance(d["messages"], list):
        d["messages"] = json.loads(d["messages"]) if d["messages"] else []
    if not isinstance(d["documents"], list):
        d["documents"] = json.loads(d["documents"]) if d["documents"] else []
    return d
