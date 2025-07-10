# app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.models.base import BaseModel
import enum


class UserStatus(enum.StrEnum):
    # 免费用户
    ACTIVE = "active"
    # 付费用户
    PAID = "paid"


class User(BaseModel):
    # 通过将 __tablename__ 设置为 app_user，我们覆盖了 SQLAlchemy 的默认表名 "user"
    # 这有助于避免与 PostgreSQL 的保留关键字 "user" 冲突
    __tablename__ = "app_user"
    email = Column(String(255), unique=True, index=True, nullable=False)
    nickname = Column(String(255), nullable=True, comment="昵称", default="大厂员工")
    avatar = Column(
        String(255),
        nullable=True,
        comment="头像",
        default="https://i-blog.csdnimg.cn/blog_migrate/94c297fce340bdcd14fbd8751677c8ff.png",
    )
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    status = Column(String(20), default="active")
    points = Column(Integer, default=0, comment="积分,用于面试支付时长")
