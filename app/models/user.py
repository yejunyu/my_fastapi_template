# app/models/user.py
from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class User(BaseModel):
    # 通过将 __tablename__ 设置为 app_user，我们覆盖了 SQLAlchemy 的默认表名 "user"
    # 这有助于避免与 PostgreSQL 的保留关键字 "user" 冲突
    __tablename__ = "app_user"

    # 邮箱字段（主要登录方式）
    email = Column(String, index=True, unique=True, nullable=False)

    # 手机号字段（可选，保留原有数据）
    phone = Column(String, index=True, unique=True, nullable=True)

    # 密码哈希
    hashed_password = Column(String, nullable=False)

    # 用户状态
    is_active = Column(Boolean, default=False, nullable=False)  # 默认未激活
    is_superuser = Column(Boolean, default=False, nullable=False)

    # 移除了与邮件验证的关系定义，不使用显式外键
