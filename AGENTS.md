# AGENTS.md — AI Agent Operating Rules & Validation Guidelines

This repository follows strict AI-assisted development standards. All AI agents, contributors, and automated tooling must adhere to the rules, schemas, testing guidelines, and workflows documented below.

---

## 1. Project Overview
- **Name:** Todo App (Tasks, Notes & Metrics)
- **Stack:** Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2, SQLite, Pytest
- **Frontend:** Responsive SPA (Tailwind CSS + Vanilla JS) served via FastAPI StaticFiles
- **Deployment:** Docker (`python:3.12-slim`) on Fly.io

---

## 2. Core Principles for AI Agents

1. **Schema-First & Validated:** All user inputs must be strictly validated via Pydantic v2 schemas before reaching business logic or database queries.
2. **Automated Verification Before Commit:** Never commit or consider a feature complete without running the full test suite (`pytest`) and verifying 100% pass rate.
3. **No Breaking Schema Changes:** API response structures must remain backward compatible. Any model change must include corresponding schema and test updates.
4. **Clean Error Contracts:** Always return predictable, structured JSON error bodies using FastAPI's `HTTPException` or validation handlers:
   ```json
   {
     "detail": "Error description or validation issues"
   }
   ```
5. **Self-Contained & Deterministic:** Tests must run against an in-memory SQLite database or isolated test fixture (`conftest.py`) without affecting development or production data.

---

## 3. Input Validation & Domain Rules

AI agents must enforce the following validation constraints across all endpoints:

### 3.1 Task Validation Rules (`schemas.TaskCreate`, `schemas.TaskUpdate`)
- **`title`**: String, required, min length 3 characters, max length 120 characters (`Field(min_length=3, max_length=120)`). Stripped of leading/trailing whitespace.
- **`description`**: String, optional, max length 1000 characters.
- **`priority`**: Enum, must be one of: `"LOW"`, `"MEDIUM"`, `"HIGH"`. Defaults to `"MEDIUM"`.
- **`status`**: Enum, must be one of: `"PENDING"`, `"IN_PROGRESS"`, `"COMPLETED"`. Defaults to `"PENDING"`.
- **`due_date`**: Optional ISO-8601 date string (`YYYY-MM-DD`).
- **`category`**: Optional string, max length 50 characters (e.g. `"Work"`, `"Personal"`, `"Urgent"`).

### 3.2 Note Validation Rules (`schemas.NoteCreate`, `schemas.NoteUpdate`)
- **`title`**: String, required, min length 1 character, max length 120 characters.
- **`content`**: String, required, min length 1 character, max length 5000 characters.
- **`tags`**: Optional list of strings (max 10 tags per note, each max 30 chars).
- **`task_id`**: Optional integer referencing an existing task ID.

### 3.3 HTTP Status Code Contracts
- `200 OK`: Successful retrieval, update, or deletion response.
- `201 Created`: Successful creation of a task or note.
- `400 Bad Request`: Invalid business logic operation or duplicate resource.
- `404 Not Found`: Requested task or note ID does not exist.
- `422 Unprocessable Entity`: Automatic Pydantic validation failure (e.g. missing fields, invalid length, invalid enum value).

---

## 4. Testing & Validation Checklist

Every agent modifying code must execute and verify the following commands before completing a task:

```bash
# 1. Run full test suite with verbose output
pytest -v

# 2. Run with coverage check (must maintain >= 90% coverage on app/)
pytest --cov=app tests/

# 3. Check code formatting / syntax
python -m py_compile app/main.py
```

### Required Test Categories:
1. **Validation Tests (`test_tasks.py`, `test_notes.py`)**:
   - Reject empty titles or titles < 3 characters.
   - Reject titles exceeding 120 characters.
   - Reject invalid enum values for `priority` and `status`.
   - Reject non-existent IDs with `404 Not Found`.
2. **State Transition Tests**:
   - Toggle task status between `PENDING` and `COMPLETED`.
   - Update task details preserving unmodified fields.
3. **Additional Features Tests (`test_extras.py`)**:
   - Search by keyword filters correctly.
   - Filter by status and priority return expected subsets.
   - Metrics endpoint returns accurate counts.
   - Backup export produces valid JSON containing tasks and notes.
   - Backup import restores data idempotently.
4. **Health Check Test**:
   - `GET /api/health` returns `{"status": "healthy"}`.

---

## 5. API Endpoints Reference

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves the web dashboard UI |
| `GET` | `/docs` | Interactive Swagger UI API documentation |
| `GET` | `/api/health` | Service health status check |
| `GET` | `/api/tasks` | List tasks (supports query params: `status`, `priority`, `search`) |
| `POST` | `/api/tasks` | Create new task (Status `201`) |
| `GET` | `/api/tasks/{id}` | Retrieve single task by ID |
| `PUT` | `/api/tasks/{id}` | Update task details |
| `PATCH` | `/api/tasks/{id}/toggle` | Toggle task completion status |
| `DELETE` | `/api/tasks/{id}` | Delete task |
| `GET` | `/api/notes` | List notes (supports query param: `search`) |
| `POST` | `/api/notes` | Create new note (Status `201`) |
| `GET` | `/api/notes/{id}` | Retrieve single note by ID |
| `PUT` | `/api/notes/{id}` | Update note |
| `DELETE` | `/api/notes/{id}` | Delete note |
| `GET` | `/api/metrics` | Summary metrics (total, pending, completed, overdue) |
| `GET` | `/api/backup/export` | Export tasks and notes as JSON |
| `POST` | `/api/backup/import` | Import tasks and notes from JSON |

---

## 6. Deployment & Container Standards
- **Containerization**: Base image `python:3.12-slim`, non-root execution where possible, dependencies installed with `--no-cache-dir`.
- **Fly.io Spec (`fly.toml`)**:
  - Expose port `8000`.
  - HTTP Health check configured on `/api/health`.
  - Graceful shutdown timeout configured.
- **Git & Commits**:
  - Keep commits atomic and descriptive with standard prefixes (`feat:`, `test:`, `docs:`, `fix:`).
