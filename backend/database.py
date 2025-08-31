from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextvars import ContextVar
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+psycopg://localhost:5432/fullstack_app')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
metadata = MetaData()

Base = declarative_base()

db_session: ContextVar[Session] = ContextVar('db_session')

def get_db_session() -> Session:
    return db_session.get()

def test_connection():
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        print("Database connected successfully")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

def run_migrations():
    from alembic.config import Config
    from alembic import command
    
    alembic_cfg = Config("alembic.ini")
    try:
        command.upgrade(alembic_cfg, "head")
        print("Database migrations completed successfully")
    except Exception as e:
        print(f"Migration failed: {e}")
        raise