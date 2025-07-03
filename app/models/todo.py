# app/models/todo.py
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Todo(BaseModel):
    __tablename__ = "todo"

    content = Column(String, index=True, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)

    # 外键，关联到 app_user 表的 id 字段
    owner_id = Column(Integer, ForeignKey("app_user.id"), nullable=True)

    # 建立与 User 模型的关系
    owner = relationship("User", back_populates="todos")
