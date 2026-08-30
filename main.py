from fastapi import FastAPI

app = FastAPI(title="Task API", version="1.0")


@app.get("/")
def root():
    """Describes the API and lists its top-level resources."""
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
def health():
    """Simple liveness check."""
    return {"status": "ok"}
