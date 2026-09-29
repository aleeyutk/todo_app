import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database import engine, Base
from app.routers import tasks, notes, extras

# Ensure all database tables exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Todo & Notes App",
    description="Full-featured Task & Notes Management with Metrics, Search & JSON Backup",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(tasks.router)
app.include_router(notes.router)
app.include_router(extras.router)

# Mount static files
static_dir = Path(__file__).resolve().parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
    def serve_home():
        return FileResponse(static_dir / "index.html")
else:
    @app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
    def home_fallback():
        return {"message": "Todo App API is running. Visit /docs for Swagger UI."}
