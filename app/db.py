import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Get the database URL from environment variables
DB_URL: str = os.environ["DB_URL"]

# Create the SQLAlchemy engine
engine = create_engine(DB_URL, future=True)

# Create a configured "SessionLocal" class
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)

# Base class for declarative class definitions.
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Provides a database session to be used as FastAPI dependency.
    
    Usage example in a FastAPI endpoint:

      from fastapi import Depends
      from app.db import get_db
      
      @app.get("/items/")
      def read_items(db: Session = Depends(get_db)):
          # use db session here
          ...
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
