# app/models/user.py
from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class User(BaseModel):
    # 通过将 __tablename__ 设置为 app_user，我们覆盖了 SQLAlchemy 的默认表名 "user"
    # 这有助于避免与 PostgreSQL 的保留关键字 "user" 冲突
    __tablename__ = "app_user"

    phone = Column(String, index=True, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # 建立与 Todo 模型的关系
    # back_populates="owner" 指定了在 Todo 模型中，哪个属性反向关联回 User
    todos = relationship("Todo", back_populates="owner")
