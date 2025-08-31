from peewee import *
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_PATH = os.getenv('DATABASE_PATH', 'fullstack_app.db')

db = SqliteDatabase(DATABASE_PATH)

class BaseModel(Model):
    class Meta:
        database = db

def connect_db():
    try:
        db.connect()
        print("Database connected successfully")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

def close_db():
    if not db.is_closed():
        db.close()
        print("Database connection closed")

def create_tables():
    from models import User, Task
    with db:
        db.create_tables([User, Task])
        print("Tables created successfully")