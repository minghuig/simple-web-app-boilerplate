from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from contextlib import asynccontextmanager

from database import connect_db, close_db, create_tables
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
    connect_db()
    create_tables()
    yield
    close_db()

app = FastAPI(title="Full Stack App API", version="1.0.0", lifespan=lifespan)

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
    try:
        new_user = User.create(username=user.username, email=user.email)
        return UserResponse(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            is_active=new_user.is_active
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/users", response_model=List[UserResponse])
def get_users():
    users = User.select()
    return [UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active
    ) for user in users]

@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    try:
        user = User.get(User.id == user_id)
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active
        )
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

# Task endpoints
@app.post("/api/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate):
    try:
        user = User.get(User.id == task.user_id)
        new_task = Task.create(
            title=task.title,
            description=task.description,
            user=user
        )
        return TaskResponse(
            id=new_task.id,
            title=new_task.title,
            description=new_task.description,
            completed=new_task.completed,
            user_id=new_task.user.id
        )
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/tasks", response_model=List[TaskResponse])
def get_tasks():
    tasks = Task.select()
    return [TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        user_id=task.user.id
    ) for task in tasks]

@app.get("/api/users/{user_id}/tasks", response_model=List[TaskResponse])
def get_user_tasks(user_id: int):
    try:
        user = User.get(User.id == user_id)
        tasks = Task.select().where(Task.user == user)
        return [TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            user_id=task.user.id
        ) for task in tasks]
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

@app.put("/api/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate):
    try:
        task = Task.get(Task.id == task_id)
        if task_update.title is not None:
            task.title = task_update.title
        if task_update.description is not None:
            task.description = task_update.description
        if task_update.completed is not None:
            task.completed = task_update.completed
        task.save()
        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            user_id=task.user.id
        )
    except Task.DoesNotExist:
        raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    try:
        task = Task.get(Task.id == task_id)
        task.delete_instance()
        return {"message": "Task deleted successfully"}
    except Task.DoesNotExist:
        raise HTTPException(status_code=404, detail="Task not found")