# 🚀 Todo & Notes App (HNG 15 Internship - Stage 1)

A clean, responsive, and robust **Task and Note Management Web Application** built with **FastAPI**, **SQLAlchemy**, **Pydantic v2**, and modern **Tailwind CSS**. Designed for containerized deployment on **Fly.io** with complete input validation, interactive OpenAPI/Swagger documentation, and an automated test suite.

---

## ✨ Key Features

1. **Task Management:**
   - Full CRUD operations with priority tags (`LOW`, `MEDIUM`, `HIGH`).
   - Lifecycle status tracking (`PENDING`, `IN_PROGRESS`, `COMPLETED`).
   - Quick one-click status toggle.
   - Due dates with visual overdue warning indicators.
   - Category filtering and real-time search across titles and descriptions.

2. **Notes System:**
   - Full CRUD notes with rich multiline content.
   - Tagging system (comma-separated chips).
   - Optional linking of notes directly to tasks.
   - Instant search across note titles, content, and tags.

3. **Bonus / Additional Features:**
   - **Real-Time Dashboard Metrics:** Total tasks, completed, pending, in progress, overdue, and overall completion rate %.
   - **JSON Backup & Restore:** One-click download of all application data, and restore via JSON upload.
   - **Interactive API Documentation:** Full Swagger UI available at `/docs` and ReDoc at `/redoc`.

---

## 🛠 Tech Stack

- **Backend:** Python 3.12, FastAPI, Uvicorn, SQLAlchemy 2.0, Pydantic v2, SQLite
- **Frontend:** Responsive Single-Page Application (HTML5, Tailwind CSS, Lucide Icons, Vanilla JS) served via FastAPI `StaticFiles`
- **Testing:** Pytest, HTTPX (`TestClient`), Pytest-Cov (17 automated tests, >90% coverage)
- **Deployment:** Docker (`python:3.12-slim`), Fly.io

---

## 🚦 Testing & Validation Rules

Strict validation is enforced on all API endpoints via Pydantic:
- Task titles require **min 3 characters**, **max 120 characters** (whitespace trimmed).
- Priority and Status are strictly checked against enum values.
- Due dates must adhere to ISO-8601 (`YYYY-MM-DD`).
- Note titles and content must not be blank.

For detailed guidelines and contributor standards, consult [`AGENTS.md`](./AGENTS.md).

---

## 💻 Local Setup & Development

### 1. Clone & Setup Virtual Environment
```bash
git clone https://github.com/aleeyutk/todo_app.git
cd todo_app

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Tests
```bash
pytest -v --cov=app tests/
```

### 3. Start Development Server
```bash
uvicorn app.main:app --reload --port 8000
```
- Open Web UI: [http://localhost:8000](http://localhost:8000)
- Open Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🐳 Docker Setup

```bash
docker build -t todo_app .
docker run -p 8000:8000 todo_app
```

---

## ☁️ Deployment (Fly.io)

```bash
flyctl deploy
```

---

## 📝 License
MIT License. Created for the HNG 15 Internship.
