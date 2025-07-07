# app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.models.base import BaseModel
import enum


class UserStatus(enum.StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class User(BaseModel):
    # 通过将 __tablename__ 设置为 app_user，我们覆盖了 SQLAlchemy 的默认表名 "user"
    # 这有助于避免与 PostgreSQL 的保留关键字 "user" 冲突
    __tablename__ = "app_user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False)
    status = Column(String(20), default="active")
