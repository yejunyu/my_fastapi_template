# app/schemas/email_verification.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.models.email_verification import VerificationType


# 用于创建邮件验证的模型
class EmailVerificationCreate(BaseModel):
    token: str
    verification_type: VerificationType
    user_id: int
    email: EmailStr
    expires_at: datetime


# 用于更新邮件验证的模型
class EmailVerificationUpdate(BaseModel):
    is_used: Optional[str] = None


# 用于返回邮件验证信息的模型
class EmailVerificationPublic(BaseModel):
    id: int
    token: str
    verification_type: VerificationType
    user_id: int
    email: EmailStr
    expires_at: datetime
    is_used: str
    created_at: datetime
