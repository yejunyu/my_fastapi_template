from datetime import datetime, timedelta
import secrets
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class PasswordResetToken(BaseModel):
    __tablename__ = "password_reset_token"

    user_id = Column(ForeignKey("app_user.id"), nullable=False)
    token = Column(String(64), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False, nullable=False)

    # 关联到用户
    user = relationship("User")

    @classmethod
    def create_token(cls, user_id: int, valid_minutes: int = 30):
        """创建密码重置token"""
        token = secrets.token_urlsafe(32)  # 生成安全的随机token
        expires_at = datetime.utcnow() + timedelta(minutes=valid_minutes)
        return cls(user_id=user_id, token=token, expires_at=expires_at, used=False)

    def is_valid(self) -> bool:
        """检查token是否有效（未使用且未过期）"""
        return not self.used and datetime.utcnow() < self.expires_at  # type: ignore

    def mark_as_used(self):
        """标记token为已使用"""
        self.used = True
