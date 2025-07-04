from datetime import datetime, timedelta
import secrets
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from .base import Base


class PasswordReset(Base):
    __tablename__ = "password_reset"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    token = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)

    @classmethod
    def create_token(cls, user_id: int, valid_minutes: int = 30):
        """创建密码重置token"""
        token = secrets.token_urlsafe(32)  # 生成安全的随机token
        expires_at = datetime.now() + timedelta(minutes=valid_minutes)
        return cls(user_id=user_id, token=token, expires_at=expires_at, used=False)

    def is_valid(self) -> bool:
        """检查token是否有效（未使用且未过期）"""
        return not self.used and datetime.now() < self.expires_at  # type: ignore

    def mark_as_used(self):
        """标记token为已使用"""
        self.used = True
