import pytest


def test_create_note_success(client):
    payload = {
        "title": "Meeting Notes",
        "content": "Discussed Fly.io deployment and Docker optimizations.",
        "tags": "devops,meeting,notes",
    }
    response = client.post("/api/notes", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["title"] == "Meeting Notes"
    assert data["content"] == payload["content"]
    assert data["tags"] == "devops,meeting,notes"
    assert data["task_id"] is None


def test_create_note_with_task_association(client):
    task_res = client.post("/api/tasks", json={"title": "Main Project Task"})
    task_id = task_res.json()["id"]

    note_res = client.post(
        "/api/notes",
        json={
            "title": "Task Implementation Details",
            "content": "Use SQLAlchemy session and Pydantic schemas",
            "task_id": task_id,
        },
    )
    assert note_res.status_code == 201
    assert note_res.json()["task_id"] == task_id


def test_create_note_with_invalid_task_id(client):
    res = client.post(
        "/api/notes",
        json={
            "title": "Invalid Note",
            "content": "Referencing non-existent task",
            "task_id": 99999,
        },
    )
    assert res.status_code == 404


def test_note_validation_failures(client):
    # Empty title
    assert client.post("/api/notes", json={"title": "", "content": "valid"}).status_code == 422

    # Whitespace title
    assert client.post("/api/notes", json={"title": "   ", "content": "valid"}).status_code == 422

    # Empty content
    assert client.post("/api/notes", json={"title": "valid", "content": ""}).status_code == 422


def test_get_and_update_note(client):
    create_res = client.post("/api/notes", json={"title": "Draft Note", "content": "Initial content"})
    note_id = create_res.json()["id"]

    # Get single
    get_res = client.get(f"/api/notes/{note_id}")
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Draft Note"

    # Update
    update_res = client.put(
        f"/api/notes/{note_id}",
        json={"title": "Published Note", "content": "Refined content", "tags": "final"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Published Note"
    assert update_res.json()["content"] == "Refined content"

    # 404 for non-existent
    assert client.get("/api/notes/99999").status_code == 404
    assert client.put("/api/notes/99999", json={"title": "None"}).status_code == 404


def test_delete_note(client):
    create_res = client.post("/api/notes", json={"title": "Temp Note", "content": "Will be deleted"})
    note_id = create_res.json()["id"]

    # Delete
    del_res = client.delete(f"/api/notes/{note_id}")
    assert del_res.status_code == 200
    assert client.get(f"/api/notes/{note_id}").status_code == 404
    assert client.delete(f"/api/notes/{note_id}").status_code == 404


def test_search_notes(client):
    client.post("/api/notes", json={"title": "Architecture Overview", "content": "Microservices vs Monolith", "tags": "arch"})
    client.post("/api/notes", json={"title": "Frontend Specs", "content": "Tailwind CSS styling", "tags": "ui"})

    res_arch = client.get("/api/notes?search=Microservices")
    assert len(res_arch.json()) == 1
    assert res_arch.json()[0]["title"] == "Architecture Overview"

    res_ui = client.get("/api/notes?search=Tailwind")
    assert len(res_ui.json()) == 1
    assert res_ui.json()[0]["title"] == "Frontend Specs"
