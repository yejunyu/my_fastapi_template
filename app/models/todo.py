# app/models/todo.py
from sqlalchemy import Column, Integer, String, Boolean
from .base import Base, BaseModel


class Todo(BaseModel):
    __tablename__ = "todo"
    title = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    completed = Column(Boolean, default=False)
    user_id = Column(Integer, nullable=False)
