#!/usr/bin/env python3
"""
Database reset script - drops all tables and recreates with migrations
Usage: python reset_db.py
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from database import DATABASE_URL
from alembic.config import Config
from alembic import command

def reset_database():
    """Drop all tables and recreate them with fresh migrations"""
    
    load_dotenv()
    
    print("🗑️  Resetting database...")
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Drop all tables in public schema
            print("Dropping all tables...")
            
            conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
            conn.execute(text("CREATE SCHEMA public"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO postgres"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO public"))
            conn.commit()
        
        print("✅ All tables dropped successfully")
        
        # Run migrations from scratch
        print("Running fresh migrations...")
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        
        print("✅ Database reset complete!")
        print("📊 Fresh tables created with latest schema")
        
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        return False
    
    return True

if __name__ == "__main__":
    reset_database()