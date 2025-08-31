from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from contextlib import asynccontextmanager

from database import run_migrations, SessionLocal, db_session, get_db_session, test_connection
from models import User, Task


class UserCreate(BaseModel):
    username: str
    email: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    user_id: int

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    completed: bool
    user_id: int


@asynccontextmanager
async def lifespan(app: FastAPI):
    test_connection()
    run_migrations()
    yield

app = FastAPI(title="Full Stack App API", version="1.0.0", lifespan=lifespan)

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    session = SessionLocal()
    db_session.set(session)
    try:
        response = await call_next(request)
        session.commit()
        return response
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI with PostgreSQL!"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "database": "connected"}

# User endpoints
@app.post("/api/users", response_model=UserResponse)
def create_user(user: UserCreate):
    db = get_db_session()
    db_user = User(username=user.username, email=user.email)
    db.add(db_user)
    db.flush()
    db.refresh(db_user)
    return UserResponse(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        is_active=db_user.is_active
    )

@app.get("/api/users", response_model=List[UserResponse])
def get_users():
    db = get_db_session()
    users = db.query(User).order_by(User.username).all()
    return [UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active
    ) for user in users]

@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    db = get_db_session()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active
    )

# Task endpoints
@app.post("/api/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate):
    db = get_db_session()
    user = db.query(User).filter(User.id == task.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_task = Task(
        title=task.title,
        description=task.description,
        user_id=task.user_id
    )
    db.add(db_task)
    db.flush()
    db.refresh(db_task)
    return TaskResponse(
        id=db_task.id,
        title=db_task.title,
        description=db_task.description,
        completed=db_task.completed,
        user_id=db_task.user_id
    )

@app.get("/api/tasks", response_model=List[TaskResponse])
def get_tasks():
    db = get_db_session()
    tasks = db.query(Task).order_by(Task.completed, Task.created_at.desc()).all()
    return [TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        user_id=task.user_id
    ) for task in tasks]

@app.get("/api/users/{user_id}/tasks", response_model=List[TaskResponse])
def get_user_tasks(user_id: int):
    db = get_db_session()
    user = db.query(User).filter(User.id == user_id).order_by(Task.completed, Task.created_at.desc()).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    tasks = db.query(Task).filter(Task.user_id == user_id).all()
    return [TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        user_id=task.user_id
    ) for task in tasks]

@app.put("/api/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate):
    db = get_db_session()
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task_update.title is not None:
        task.title = task_update.title
    if task_update.description is not None:
        task.description = task_update.description
    if task_update.completed is not None:
        task.completed = task_update.completed
    
    db.flush()
    db.refresh(task)
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        user_id=task.user_id
    )

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    db = get_db_session()
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    return {"message": "Task deleted successfully"}