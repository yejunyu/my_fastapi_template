# app/schemas/user.py
from typing import Optional
from pydantic import BaseModel, EmailStr

from app.models.user import UserStatus


# 用于发送验证码的模型
class SendVerificationCode(BaseModel):
    email: EmailStr


# 用于创建新用户的模型，包含了密码和验证码
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    verification_code: str


# 用于登录的模型
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# 用于更新用户的模型，所有字段都可选
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None  # 如果提供，将被哈希处理
    status: Optional[UserStatus] = None
    is_superuser: Optional[bool] = None


# 用于从 API 返回用户信息的模型，不应包含密码
class UserPublic(BaseModel):
    id: int
    email: str
    status: UserStatus
    is_superuser: bool


# 用于忘记密码的模型
class ForgotPassword(BaseModel):
    email: EmailStr


# 用于重置密码的模型
class ResetPassword(BaseModel):
    token: str
    new_password: str
