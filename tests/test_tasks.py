import pytest


def test_create_task_success(client):
    payload = {
        "title": "Complete Stage 1 Task",
        "description": "Build and deploy todo app",
        "priority": "HIGH",
        "status": "PENDING",
        "due_date": "2026-10-15",
        "category": "Internship",
    }
    response = client.post("/api/tasks", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["title"] == "Complete Stage 1 Task"
    assert data["priority"] == "HIGH"
    assert data["status"] == "PENDING"
    assert data["due_date"] == "2026-10-15"
    assert data["category"] == "Internship"


def test_create_task_validation_failures(client):
    # Short title (< 3 chars)
    res = client.post("/api/tasks", json={"title": "ab"})
    assert res.status_code == 422

    # Whitespace only title (< 3 chars stripped)
    res = client.post("/api/tasks", json={"title": "   "})
    assert res.status_code == 422

    # Excessively long title (> 120 chars)
    res = client.post("/api/tasks", json={"title": "A" * 121})
    assert res.status_code == 422

    # Invalid priority enum
    res = client.post("/api/tasks", json={"title": "Valid Title", "priority": "URGENT"})
    assert res.status_code == 422

    # Invalid status enum
    res = client.post("/api/tasks", json={"title": "Valid Title", "status": "UNKNOWN"})
    assert res.status_code == 422

    # Invalid due date format
    res = client.post("/api/tasks", json={"title": "Valid Title", "due_date": "15-10-2026"})
    assert res.status_code == 422


def test_get_task_by_id(client):
    # Create task
    create_res = client.post("/api/tasks", json={"title": "Test Single Get"})
    task_id = create_res.json()["id"]

    # Get success
    get_res = client.get(f"/api/tasks/{task_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == task_id
    assert get_res.json()["title"] == "Test Single Get"

    # Get non-existent
    not_found_res = client.get("/api/tasks/99999")
    assert not_found_res.status_code == 404


def test_update_task(client):
    create_res = client.post("/api/tasks", json={"title": "Original Title", "priority": "LOW"})
    task_id = create_res.json()["id"]

    # Update title and priority
    update_res = client.put(
        f"/api/tasks/{task_id}",
        json={"title": "Updated Title", "priority": "HIGH", "status": "IN_PROGRESS"},
    )
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["title"] == "Updated Title"
    assert data["priority"] == "HIGH"
    assert data["status"] == "IN_PROGRESS"

    # Update non-existent
    res_404 = client.put("/api/tasks/99999", json={"title": "Non-existent"})
    assert res_404.status_code == 404


def test_toggle_task_status(client):
    create_res = client.post("/api/tasks", json={"title": "Toggle Me", "status": "PENDING"})
    task_id = create_res.json()["id"]

    # Toggle 1: PENDING -> COMPLETED
    toggle_1 = client.patch(f"/api/tasks/{task_id}/toggle")
    assert toggle_1.status_code == 200
    assert toggle_1.json()["status"] == "COMPLETED"

    # Toggle 2: COMPLETED -> PENDING
    toggle_2 = client.patch(f"/api/tasks/{task_id}/toggle")
    assert toggle_2.status_code == 200
    assert toggle_2.json()["status"] == "PENDING"

    # Toggle non-existent
    assert client.patch("/api/tasks/99999/toggle").status_code == 404


def test_delete_task(client):
    create_res = client.post("/api/tasks", json={"title": "To be deleted"})
    task_id = create_res.json()["id"]

    # Delete
    del_res = client.delete(f"/api/tasks/{task_id}")
    assert del_res.status_code == 200

    # Ensure it's gone
    assert client.get(f"/api/tasks/{task_id}").status_code == 404

    # Delete non-existent
    assert client.delete(f"/api/tasks/{task_id}").status_code == 404


def test_list_tasks_and_filtering(client):
    # Setup test tasks
    client.post("/api/tasks", json={"title": "Learn FastAPI", "priority": "HIGH", "status": "COMPLETED", "category": "Backend"})
    client.post("/api/tasks", json={"title": "Write Dockerfile", "priority": "MEDIUM", "status": "PENDING", "category": "DevOps"})
    client.post("/api/tasks", json={"title": "Deploy on Fly.io", "priority": "HIGH", "status": "PENDING", "category": "DevOps"})

    # All tasks
    all_res = client.get("/api/tasks")
    assert len(all_res.json()) == 3

    # Filter by status
    pending_res = client.get("/api/tasks?status=PENDING")
    assert len(pending_res.json()) == 2

    # Filter by priority
    high_res = client.get("/api/tasks?priority=HIGH")
    assert len(high_res.json()) == 2

    # Filter by category
    devops_res = client.get("/api/tasks?category=DevOps")
    assert len(devops_res.json()) == 2

    # Search keyword
    search_res = client.get("/api/tasks?search=FastAPI")
    assert len(search_res.json()) == 1
    assert search_res.json()[0]["title"] == "Learn FastAPI"
