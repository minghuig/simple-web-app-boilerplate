import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database import Base, db_session
from models import User, Task  # Import models so they're registered

# Test database URL (use separate test database)
TEST_DATABASE_URL = "postgresql+psycopg://localhost:5432/fullstack_app_test"

# Create test database if it doesn't exist
def create_test_database():
    from sqlalchemy import create_engine, text
    admin_engine = create_engine("postgresql+psycopg://localhost:5432/postgres")
    with admin_engine.connect() as conn:
        conn.execute(text("COMMIT"))  # End any existing transaction
        try:
            conn.execute(text("CREATE DATABASE fullstack_app_test"))
        except Exception:
            pass  # Database already exists
    admin_engine.dispose()

@pytest.fixture(scope="session")
def test_engine():
    create_test_database()
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_db(test_engine):
    # Clean database before each test (ignore errors if tables don't exist yet)
    with test_engine.connect() as conn:
        try:
            conn.execute(text("DELETE FROM tasks"))
            conn.execute(text("DELETE FROM users"))
            conn.execute(text("ALTER SEQUENCE tasks_id_seq RESTART WITH 1"))
            conn.execute(text("ALTER SEQUENCE users_id_seq RESTART WITH 1"))
            conn.commit()
        except Exception:
            conn.rollback()  # Ignore cleanup errors on first run
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    
    # Set the session in context
    token = db_session.set(session)
    
    yield session
    
    session.close()
    db_session.reset(token)

@pytest.fixture(scope="function")
def client(test_db):
    # Create a test app instance without lifespan to avoid database migrations
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from main import (UserCreate, UserResponse, TaskCreate, TaskUpdate, TaskResponse,
                     create_user, get_users, get_user, create_task, get_tasks, 
                     get_user_tasks, update_task, delete_task, read_root, health_check)
    
    test_app = FastAPI(title="Test API")
    
    # Add CORS middleware
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add routes without database middleware
    test_app.get("/")(read_root)
    test_app.get("/api/health")(health_check)
    test_app.post("/api/users", response_model=UserResponse)(create_user)
    test_app.get("/api/users", response_model=list[UserResponse])(get_users)
    test_app.get("/api/users/{user_id}", response_model=UserResponse)(get_user)
    test_app.post("/api/tasks", response_model=TaskResponse)(create_task)
    test_app.get("/api/tasks", response_model=list[TaskResponse])(get_tasks)
    test_app.get("/api/users/{user_id}/tasks", response_model=list[TaskResponse])(get_user_tasks)
    test_app.put("/api/tasks/{task_id}", response_model=TaskResponse)(update_task)
    test_app.delete("/api/tasks/{task_id}")(delete_task)
    
    with TestClient(test_app) as test_client:
        yield test_client

@pytest.fixture(scope="function")
def sample_user(client):
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    response = client.post("/api/users", json={
        "username": f"testuser_{unique_id}",
        "email": f"test_{unique_id}@example.com"
    })
    return response.json()