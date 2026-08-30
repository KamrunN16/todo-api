from typing import Optional

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title="Task API", version="1.0")

# In-memory "database" - resets every time the server restarts.
tasks = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Write report", "done": False},
    {"id": 3, "title": "Call plumber", "done": True},
]
next_id = 4


class TaskCreate(BaseModel):
    title: str = ""


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


def find_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Every 4xx/5xx in this API is shaped as {"error": "..."} per spec."""
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.get("/", tags=["meta"], summary="API description")
def root():
    """Describes the API and lists its top-level resources."""
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health", tags=["meta"], summary="Liveness check")
def health():
    """Simple liveness check used for uptime/monitoring."""
    return {"status": "ok"}


@app.get("/tasks", tags=["tasks"], summary="List tasks")
def list_tasks(
    done: Optional[bool] = None,
    search: Optional[str] = None,
    limit: Optional[int] = None,
    offset: int = 0,
):
    """Return every task, optionally filtered/searched/paginated.

    - **done**: filter by completion status (true/false)
    - **search**: only tasks whose title contains this text (case-insensitive)
    - **limit** / **offset**: simple pagination
    """
    result = tasks
    if done is not None:
        result = [t for t in result if t["done"] == done]
    if search:
        result = [t for t in result if search.lower() in t["title"].lower()]
    if limit is not None:
        result = result[offset: offset + limit]
    elif offset:
        result = result[offset:]
    return result


@app.get("/tasks/{task_id}", tags=["tasks"], summary="Get one task")
def get_task(task_id: int):
    """Return a single task by id, or 404 if it doesn't exist."""
    task = find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


@app.post("/tasks", status_code=201, tags=["tasks"], summary="Create a task")
def create_task(payload: TaskCreate):
    """Create a task. `title` is required and cannot be empty/blank -> 400 if it is."""
    global next_id
    title = payload.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="title is required and cannot be empty")
    task = {"id": next_id, "title": title, "done": False}
    tasks.append(task)
    next_id += 1
    return task


@app.put("/tasks/{task_id}", tags=["tasks"], summary="Update a task")
def update_task(task_id: int, payload: TaskUpdate):
    """Replace a task's title and/or done. Unknown id -> 404, empty/invalid body -> 400."""
    task = find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    if payload.title is None and payload.done is None:
        raise HTTPException(status_code=400, detail="provide at least title or done to update")

    if payload.title is not None:
        title = payload.title.strip()
        if not title:
            raise HTTPException(status_code=400, detail="title cannot be empty")
        task["title"] = title

    if payload.done is not None:
        task["done"] = payload.done

    return task


@app.delete("/tasks/{task_id}", status_code=204, tags=["tasks"], summary="Delete a task")
def delete_task(task_id: int):
    """Remove a task. Unknown id -> 404. Success returns 204 with no body."""
    task = find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    tasks.remove(task)
    return Response(status_code=204)


@app.get("/stats", tags=["extras"], summary="Task counts")
def stats():
    """A tiny computed view: total / done / open counts."""
    total = len(tasks)
    done_count = sum(1 for t in tasks if t["done"])
    return {"total": total, "done": done_count, "open": total - done_count}


@app.post("/reset", tags=["extras"], summary="Reset to seed data")
def reset():
    """Restore the original 3 example tasks. Handy for demos."""
    global tasks, next_id
    tasks = [
        {"id": 1, "title": "Buy groceries", "done": False},
        {"id": 2, "title": "Write report", "done": False},
        {"id": 3, "title": "Call plumber", "done": True},
    ]
    next_id = 4
    return {"message": "reset to seed data", "tasks": tasks}
