from fastapi import FastAPI, HTTPException
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


@app.get("/")
def root():
    """Describes the API and lists its top-level resources."""
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
def health():
    """Simple liveness check."""
    return {"status": "ok"}


@app.get("/tasks")
def list_tasks():
    """Return every task."""
    return tasks


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    """Return a single task by id, or 404 if it doesn't exist."""
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


@app.post("/tasks", status_code=201)
def create_task(payload: TaskCreate):
    """Create a task. title is required and cannot be empty/blank."""
    global next_id
    title = payload.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="title is required and cannot be empty")
    task = {"id": next_id, "title": title, "done": False}
    tasks.append(task)
    next_id += 1
    return task
