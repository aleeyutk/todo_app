from datetime import datetime, timezone, date
from typing import Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Task, Note, Status
from app.schemas import MetricsResponse, BackupData, TaskResponse, NoteResponse

router = APIRouter(prefix="/api", tags=["Extras"])


@router.api_route("/health", methods=["GET", "HEAD"], status_code=status.HTTP_200_OK)
def health_check():
    return {
        "status": "healthy",
        "service": "todo-app",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
    }


@router.get("/metrics", response_model=MetricsResponse)
def get_metrics(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.status == Status.COMPLETED.value)
    pending_tasks = sum(1 for t in tasks if t.status == Status.PENDING.value)
    in_progress_tasks = sum(1 for t in tasks if t.status == Status.IN_PROGRESS.value)

    today_str = date.today().isoformat()
    overdue_tasks = sum(
        1
        for t in tasks
        if t.status != Status.COMPLETED.value
        and t.due_date is not None
        and t.due_date < today_str
    )

    total_notes = db.query(Note).count()

    completion_rate = (
        round((completed_tasks / total_tasks) * 100, 1) if total_tasks > 0 else 0.0
    )

    return MetricsResponse(
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        in_progress_tasks=in_progress_tasks,
        overdue_tasks=overdue_tasks,
        total_notes=total_notes,
        completion_rate_percentage=completion_rate,
    )


@router.get("/backup/export", response_model=BackupData)
def export_backup(db: Session = Depends(get_db)):
    tasks = db.query(Task).order_by(Task.id.asc()).all()
    notes = db.query(Note).order_by(Note.id.asc()).all()

    return BackupData(
        version="1.0",
        exported_at=datetime.now(timezone.utc).isoformat(),
        tasks=[TaskResponse.model_validate(t) for t in tasks],
        notes=[NoteResponse.model_validate(n) for n in notes],
    )


@router.post("/backup/import", status_code=status.HTTP_200_OK)
def import_backup(data: BackupData, db: Session = Depends(get_db)):
    imported_tasks = 0
    imported_notes = 0

    # Map old task IDs to new task IDs for relationship preservation
    task_id_map: Dict[int, int] = {}

    for t_data in data.tasks:
        task = Task(
            title=t_data.title,
            description=t_data.description,
            priority=t_data.priority.value,
            status=t_data.status.value,
            due_date=t_data.due_date,
            category=t_data.category,
        )
        db.add(task)
        db.flush()
        task_id_map[t_data.id] = task.id
        imported_tasks += 1

    for n_data in data.notes:
        new_task_id = (
            task_id_map.get(n_data.task_id) if n_data.task_id is not None else None
        )
        note = Note(
            title=n_data.title,
            content=n_data.content,
            tags=n_data.tags,
            task_id=new_task_id,
        )
        db.add(note)
        imported_notes += 1

    db.commit()

    return {
        "message": "Backup imported successfully",
        "imported_tasks": imported_tasks,
        "imported_notes": imported_notes,
    }
