"""
Database Session and Engine Configuration
Configures SQLAlchemy engine, session factory, base model, and FastAPI dependency.
"""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from app.core.config import settings

# 1. Create the SQLAlchemy Engine
# connect_args={"check_same_thread": False} is required only for SQLite
# because SQLite by default prohibits multiple threads from sharing the same connection.
# FastAPI serves requests across multiple threads concurrently.
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False  # Set to True if you wish to see raw SQL statements logged to console
)

# 2. Create the SessionLocal Factory
# autocommit=False: Changes are only saved when explicitly calling db.commit()
# autoflush=False: Queries do not auto-flush uncommitted memory states
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Base class for all SQLAlchemy ORM models
Base = declarative_base()


# 4. FastAPI Dependency: Yields a database session per HTTP request
# Guarantees that db.close() is always executed inside a finally block.
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
