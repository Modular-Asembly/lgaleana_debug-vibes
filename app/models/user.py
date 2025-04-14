from sqlalchemy import Column, Integer, String, JSON
from app.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    raw_data = Column(JSON, nullable=False)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, github_id='{self.github_id}', email='{self.email}')>"
