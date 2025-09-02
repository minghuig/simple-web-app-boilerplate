import pytest

def test_create_task(client, sample_user):
    user_id = sample_user["id"]
    response = client.post("/api/tasks", json={
        "title": "Test Task",
        "description": "This is a test task",
        "user_id": user_id
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "This is a test task"
    assert data["completed"] == False
    assert data["user_id"] == user_id
    assert "id" in data

def test_create_task_nonexistent_user(client):
    response = client.post("/api/tasks", json={
        "title": "Test Task",
        "description": "This should fail",
        "user_id": 999
    })
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

def test_create_task_minimal(client, sample_user):
    user_id = sample_user["id"]
    response = client.post("/api/tasks", json={
        "title": "Minimal Task",
        "user_id": user_id
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Minimal Task"
    assert data["description"] is None
    assert data["completed"] == False

def test_get_tasks_empty(client):
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert response.json() == []

def test_get_tasks_with_data(client, sample_user):
    user_id = sample_user["id"]
    
    # Create a task first
    client.post("/api/tasks", json={
        "title": "Test Task",
        "description": "Test description",
        "user_id": user_id
    })
    
    response = client.get("/api/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Task"

def test_get_user_tasks(client, sample_user):
    user_id = sample_user["id"]
    
    # Create multiple tasks
    client.post("/api/tasks", json={"title": "Task 1", "user_id": user_id})
    client.post("/api/tasks", json={"title": "Task 2", "user_id": user_id})
    
    response = client.get(f"/api/users/{user_id}/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_get_user_tasks_nonexistent_user(client):
    response = client.get("/api/users/999/tasks")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

def test_update_task(client, sample_user):
    user_id = sample_user["id"]
    
    # Create a task
    create_response = client.post("/api/tasks", json={
        "title": "Original Task",
        "description": "Original description",
        "user_id": user_id
    })
    task_id = create_response.json()["id"]
    
    # Update the task
    response = client.put(f"/api/tasks/{task_id}", json={
        "title": "Updated Task",
        "description": "Updated description",
        "completed": True
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Task"
    assert data["description"] == "Updated description"
    assert data["completed"] == True

def test_update_task_partial(client, sample_user):
    user_id = sample_user["id"]
    
    # Create a task
    create_response = client.post("/api/tasks", json={
        "title": "Original Task",
        "user_id": user_id
    })
    task_id = create_response.json()["id"]
    
    # Update only completed status
    response = client.put(f"/api/tasks/{task_id}", json={
        "completed": True
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Original Task"  # Unchanged
    assert data["completed"] == True  # Changed

def test_update_task_not_found(client):
    response = client.put("/api/tasks/999", json={
        "completed": True
    })
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

def test_delete_task(client, sample_user):
    user_id = sample_user["id"]
    
    # Create a task
    create_response = client.post("/api/tasks", json={
        "title": "Task to Delete",
        "user_id": user_id
    })
    task_id = create_response.json()["id"]
    
    # Delete the task
    response = client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Task deleted successfully"
    
    # Verify it's deleted
    get_response = client.get(f"/api/tasks")
    assert len(get_response.json()) == 0

def test_delete_task_not_found(client):
    response = client.delete("/api/tasks/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"