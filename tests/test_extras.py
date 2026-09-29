import pytest
from datetime import date, timedelta


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "todo-app"
    assert "timestamp" in data


def test_metrics_calculation(client):
    today = date.today()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)

    # 1 Completed task
    client.post("/api/tasks", json={"title": "Completed Task", "status": "COMPLETED"})

    # 1 Pending overdue task
    client.post(
        "/api/tasks",
        json={"title": "Overdue Task", "status": "PENDING", "due_date": yesterday.isoformat()},
    )

    # 1 In Progress task due tomorrow
    client.post(
        "/api/tasks",
        json={"title": "Ongoing Task", "status": "IN_PROGRESS", "due_date": tomorrow.isoformat()},
    )

    # 1 Note
    client.post("/api/notes", json={"title": "Quick Note", "content": "Just a note"})

    res = client.get("/api/metrics")
    assert res.status_code == 200
    metrics = res.json()

    assert metrics["total_tasks"] == 3
    assert metrics["completed_tasks"] == 1
    assert metrics["pending_tasks"] == 1
    assert metrics["in_progress_tasks"] == 1
    assert metrics["overdue_tasks"] == 1
    assert metrics["total_notes"] == 1
    # 1 out of 3 = 33.3%
    assert metrics["completion_rate_percentage"] == 33.3


def test_backup_export_and_import(client):
    # Seed data
    task_res = client.post("/api/tasks", json={"title": "Task To Export", "priority": "HIGH"})
    task_id = task_res.json()["id"]

    client.post(
        "/api/notes",
        json={"title": "Note To Export", "content": "Note Content", "task_id": task_id},
    )

    # Export
    export_res = client.get("/api/backup/export")
    assert export_res.status_code == 200
    backup_data = export_res.json()
    assert len(backup_data["tasks"]) == 1
    assert len(backup_data["notes"]) == 1

    # Import into client
    import_res = client.post("/api/backup/import", json=backup_data)
    assert import_res.status_code == 200
    assert import_res.json()["imported_tasks"] == 1
    assert import_res.json()["imported_notes"] == 1

    # Total should now be 2 tasks and 2 notes
    assert len(client.get("/api/tasks").json()) == 2
    assert len(client.get("/api/notes").json()) == 2
