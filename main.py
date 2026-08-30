from typing import Optional

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from db import get_conn, init_db

app = FastAPI(title="Task API", version="2.0")

# Data now lives in tasks.db (SQLite) instead of an in-memory list.
# The table is created automatically, and seeded once, on startup.
init_db()

class TaskCreate(BaseModel):
    title: str = ""


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


def row_to_task(row):
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


def find_task(conn, task_id: int):
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return row_to_task(row) if row else None


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.get("/", tags=["meta"], summary="API description")
def root():
    return {"name": "Task API", "version": "2.0", "endpoints": ["/tasks"]}


@app.get("/health", tags=["meta"], summary="Liveness check")
def health():
    return {"status": "ok"}


@app.get("/tasks", tags=["tasks"], summary="List tasks")
def list_tasks(
    done: Optional[bool] = None,
    search: Optional[str] = None,
    limit: Optional[int] = None,
    offset: int = 0,
):
    """Now reads from SQLite instead of the in-memory list (Stage 1)."""
    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if done is not None:
        query += " AND done = ?"
        params.append(1 if done else 0)

    if search:
        query += " AND title LIKE ? COLLATE NOCASE"
        params.append(f"%{search}%")

    query += " ORDER BY id"

    if limit is not None:
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
    elif offset:
        query += " LIMIT -1 OFFSET ?"
        params.append(offset)

    conn = get_conn()
    try:
        rows = conn.execute(query, params).fetchall()
        return [row_to_task(r) for r in rows]
    finally:
        conn.close()


@app.get("/tasks/{task_id}", tags=["tasks"], summary="Get one task")
def get_task(task_id: int):
    """Now reads from SQLite instead of the in-memory list (Stage 1)."""
    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        return row_to_task(row)
    finally:
        conn.close()


@app.post("/tasks", status_code=201, tags=["tasks"], summary="Create a task")
def create_task(payload: TaskCreate):
    """Now inserts a row into SQLite instead of pushing onto the list (Stage 2)."""
    title = payload.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="title is required and cannot be empty")

    conn = get_conn()
    try:
        cur = conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (title, 0))
        conn.commit()
        return {"id": cur.lastrowid, "title": title, "done": False}
    finally:
        conn.close()


@app.put("/tasks/{task_id}", tags=["tasks"], summary="Update a task")
def update_task(task_id: int, payload: TaskUpdate):
    """Now runs an UPDATE against SQLite instead of mutating the list (Stage 3)."""
    conn = get_conn()
    try:
        task = find_task(conn, task_id)
        if task is None:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        if payload.title is None and payload.done is None:
            raise HTTPException(status_code=400, detail="provide at least title or done to update")

        new_title = task["title"]
        if payload.title is not None:
            new_title = payload.title.strip()
            if not new_title:
                raise HTTPException(status_code=400, detail="title cannot be empty")

        new_done = task["done"] if payload.done is None else payload.done

        conn.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
            (new_title, 1 if new_done else 0, task_id),
        )
        conn.commit()
        return {"id": task_id, "title": new_title, "done": bool(new_done)}
    finally:
        conn.close()


@app.delete("/tasks/{task_id}", status_code=204, tags=["tasks"], summary="Delete a task")
def delete_task(task_id: int):
    """Now runs a DELETE against SQLite instead of removing from the list (Stage 3)."""
    conn = get_conn()
    try:
        task = find_task(conn, task_id)
        if task is None:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        return Response(status_code=204)
    finally:
        conn.close()


@app.get("/stats", tags=["extras"], summary="Task counts")
def stats():
    """A tiny computed view: total / done / open counts, computed by SQL."""
    conn = get_conn()
    try:
        total = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        done_count = conn.execute("SELECT COUNT(*) FROM tasks WHERE done = 1").fetchone()[0]
        return {"total": total, "done": done_count, "open": total - done_count}
    finally:
        conn.close()


@app.post("/reset", tags=["extras"], summary="Reset to seed data")
def reset():
    """Wipe the table and restore the original 3 example tasks. Handy for demos."""
    conn = get_conn()
    try:
        conn.execute("DELETE FROM tasks")
        conn.execute("DELETE FROM sqlite_sequence WHERE name = 'tasks'")
        conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Buy groceries", 0))
        conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Write report", 0))
        conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Call plumber", 1))
        conn.commit()
        rows = conn.execute("SELECT * FROM tasks ORDER BY id").fetchall()
        return {"message": "reset to seed data", "tasks": [row_to_task(r) for r in rows]}
    finally:
        conn.close()
