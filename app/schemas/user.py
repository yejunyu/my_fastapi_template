# app/schemas/user.py
from typing import Optional
from pydantic import BaseModel, EmailStr


# 用于创建新用户的模型（邮箱注册）
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    phone: Optional[str] = None  # 手机号可选


# 用于邮箱登录的模型
class UserEmailLogin(BaseModel):
    email: EmailStr
    password: str


# 用于密码重置请求的模型
class PasswordResetRequest(BaseModel):
    email: EmailStr


# 用于密码重置确认的模型
class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


# 用于更新用户的模型，所有字段都可选
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: Optional[str] = None  # 如果提供，将被哈希处理
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


# 用于从 API 返回用户信息的模型，不应包含密码
class UserPublic(BaseModel):
    id: int
    email: str
    phone: Optional[str] = None
    is_active: bool
    is_superuser: bool


# 用于响应消息的模型
class UserResponse(BaseModel):
    message: str
    email: Optional[str] = None
