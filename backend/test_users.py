import pytest

def test_create_user(client):
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    response = client.post("/api/users", json={
        "username": f"newuser_{unique_id}",
        "email": f"newuser_{unique_id}@example.com"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == f"newuser_{unique_id}"
    assert data["email"] == f"newuser_{unique_id}@example.com"
    assert data["is_active"] == True
    assert "id" in data

def test_create_user_duplicate_username(client, sample_user):
    response = client.post("/api/users", json={
        "username": sample_user["username"],  # Same as sample_user
        "email": "different@example.com"
    })
    assert response.status_code == 400

def test_create_user_duplicate_email(client, sample_user):
    response = client.post("/api/users", json={
        "username": "differentuser",
        "email": sample_user["email"]  # Same as sample_user
    })
    assert response.status_code == 400

def test_get_users_empty(client):
    response = client.get("/api/users")
    assert response.status_code == 200
    assert response.json() == []

def test_get_users_with_data(client, sample_user):
    response = client.get("/api/users")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["username"] == sample_user["username"]

def test_get_user_by_id(client, sample_user):
    user_id = sample_user["id"]
    response = client.get(f"/api/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["username"] == sample_user["username"]
    assert data["email"] == sample_user["email"]

def test_get_user_not_found(client):
    response = client.get("/api/users/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

def test_create_user_invalid_data(client):
    response = client.post("/api/users", json={
        "username": "",  # Empty username
        "email": "test@example.com"
    })
    assert response.status_code == 422  # Validation error