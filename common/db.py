# common/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Database URL - using PostgreSQL from docker-compose
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/backend")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
