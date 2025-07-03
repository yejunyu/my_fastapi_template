# app/schemas/user.py
from typing import Optional
from pydantic import BaseModel


# 用于创建新用户的模型，包含了密码
class UserCreate(BaseModel):
    phone: str
    password: str


# 用于更新用户的模型，所有字段都可选
class UserUpdate(BaseModel):
    phone: Optional[str] = None
    password: Optional[str] = None  # 如果提供，将被哈希处理
    is_superuser: Optional[bool] = None


# 用于从 API 返回用户信息的模型，不应包含密码
class UserPublic(BaseModel):
    id: int
    phone: str
    is_superuser: bool
