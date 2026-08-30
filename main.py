from fastapi import FastAPI, HTTPException

app = FastAPI(title="Task API", version="1.0")

# In-memory "database" - resets every time the server restarts.
tasks = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Write report", "done": False},
    {"id": 3, "title": "Call plumber", "done": True},
]
next_id = 4


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
