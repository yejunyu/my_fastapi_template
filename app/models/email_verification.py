from datetime import datetime, timedelta, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.models.base import BaseModel


class EmailVerificationCode(BaseModel):
    __tablename__ = "email_verification_code"

    email = Column(String, index=True, nullable=False)
    code = Column(String(6), nullable=False)  # 6位验证码
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False, nullable=False)

    @classmethod
    def create_code(cls, email: str, code: str, valid_minutes: int = 10):
        """创建验证码记录"""
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=valid_minutes)
        return cls(email=email, code=code, expires_at=expires_at, used=False)

    def is_valid(self) -> bool:
        """检查验证码是否有效（未使用且未过期）"""
        return not self.used and datetime.now() < self.expires_at  # type: ignore

    def mark_as_used(self):
        """标记验证码为已使用"""
        self.used = True


class EmailVerification(BaseModel):
    __tablename__ = "email_verification"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False)
    code = Column(String(10), nullable=False)
    created_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    user_id = Column(Integer, nullable=True)
