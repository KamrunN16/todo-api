# Task API

A small in-memory CRUD API for managing a to-do list, built with **FastAPI**. It supports
creating, reading, updating and deleting tasks, and ships with interactive Swagger docs.

Data lives only in memory — restarting the server resets it to the 3 seed tasks (or hit
`POST /reset` to restore them without restarting).

## Install & run

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Then open **http://localhost:8000** in your browser, or **http://localhost:8000/docs** for
the interactive Swagger UI.

## Endpoints

| Method | Path            | Description                              | Success | Errors |
|--------|-----------------|-------------------------------------------|---------|--------|
| GET    | `/`             | API description                           | 200     | —      |
| GET    | `/health`       | Liveness check                            | 200     | —      |
| GET    | `/tasks`        | List all tasks (supports filters below)   | 200     | —      |
| GET    | `/tasks/{id}`   | Get one task                              | 200     | 404    |
| POST   | `/tasks`        | Create a task (`{"title": "..."}`)        | 201     | 400    |
| PUT    | `/tasks/{id}`   | Update a task's `title` and/or `done`     | 200     | 400, 404 |
| DELETE | `/tasks/{id}`   | Delete a task                             | 204     | 404    |
| GET    | `/stats`        | *(extra)* `{ total, done, open }` counts  | 200     | —      |
| POST   | `/reset`        | *(extra)* Restore the 3 seed tasks        | 200     | —      |

`GET /tasks` also accepts optional query parameters:
- `?done=true` / `?done=false` — filter by completion status
- `?search=milk` — only tasks whose title contains the text
- `?limit=2&offset=2` — pagination (real APIs never return "everything" at once — limits
  keep responses fast and predictable as the list grows)

Every error response is shaped as `{ "error": "..." }`.

## Example: `curl -i`

```
$ curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Buy milk"}'

HTTP/1.1 201 Created
date: Sun, 30 Aug 2026 05:15:23 GMT
server: uvicorn
content-length: 40
content-type: application/json

{"id":4,"title":"Buy milk","done":false}
```

## Swagger UI

`/docs` lists every endpoint and lets you run the full CRUD cycle with "Try it out" —
no curl needed.

> **Add your screenshot here:** run the server, open `http://localhost:8000/docs`,
> and paste a screenshot of the page into this section before you submit.

![Swagger UI screenshot](swagger-screenshot.png)

## The mortality experiment

Create a few tasks, restart the server, then `GET /tasks` — the new tasks are gone and
you're back to the 3 seed tasks. That's because everything lives in a plain Python list
in memory: it only exists for as long as the process runs. Fixing this — making data
survive a restart — is what a real database is for, which is next week's topic.

## Project structure

```
.
├── main.py           # the whole API
├── requirements.txt
└── README.md
```
