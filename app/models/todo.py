# app/models/todo.py
from sqlalchemy import Column, Integer, String, Boolean
from .base import Base


class Todo(Base):
    __tablename__ = "todo"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    completed = Column(Boolean, default=False)
    user_id = Column(Integer, nullable=False)
