from datetime import datetime, timedelta
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Enum
from sqlalchemy.orm import relationship
import enum
import uuid

from app.models.base import BaseModel


class VerificationType(str, enum.Enum):
    """验证类型枚举"""

    ACTIVATION = "activation"  # 账户激活
    PASSWORD_RESET = "password_reset"  # 密码重置


class EmailVerification(BaseModel):
    """邮件验证模型"""

    __tablename__ = "email_verification"

    # 验证token，使用UUID确保唯一性
    token = Column(String, unique=True, nullable=False, index=True)

    # 验证类型
    verification_type = Column(Enum(VerificationType), nullable=False)

    # 关联的用户ID
    user_id = Column(Integer, nullable=False)

    # 邮箱地址（冗余存储，便于查询和验证）
    email = Column(String, nullable=False)

    # 过期时间
    expires_at = Column(DateTime, nullable=False)

    # 是否已使用
    is_used = Column(
        String, default="false", nullable=False
    )  # 使用字符串避免数据库兼容性问题

    # 移除了关联用户的关系定义，不使用显式外键

    @classmethod
    def create_token(
        cls,
        user_id: int,
        email: str,
        verification_type: VerificationType,
        expire_hours: int = 2,
    ):
        """创建验证token"""
        return cls(
            token=str(uuid.uuid4()),
            verification_type=verification_type,
            user_id=user_id,
            email=email,
            expires_at=datetime.now() + timedelta(hours=expire_hours),
            is_used="false",
        )

    def is_expired(self) -> bool:
        """检查是否过期"""
        now = datetime.now()
        return bool(now > self.expires_at)

    def mark_as_used(self):
        """标记为已使用"""
        self.is_used = "true"
