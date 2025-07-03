from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models
from app.core.security import verify_password


class AuthenticationStrategy(ABC):
    """认证策略接口"""

    @abstractmethod
    async def authenticate(
        self, db: AsyncSession, **credentials
    ) -> Optional[models.User]:
        """认证用户"""
        pass


class EmailPasswordAuth(AuthenticationStrategy):
    """邮箱密码认证策略"""

    async def authenticate(
        self, db: AsyncSession, **credentials
    ) -> Optional[models.User]:
        """通过邮箱和密码认证用户"""
        email = credentials.get("email")
        password = credentials.get("password")

        if not email or not password:
            return None

        user = await crud.user.get_by_email(db, email=email)
        if not user:
            return None

        if not verify_password(password, str(user.hashed_password)):
            return None

        # 检查用户状态是否为激活
        if user.status != models.UserStatus.ACTIVE:
            return None

        return user


class PhoneCodeAuth(AuthenticationStrategy):
    """手机验证码认证策略（预留）"""

    async def authenticate(
        self, db: AsyncSession, **credentials
    ) -> Optional[models.User]:
        """通过手机号和验证码认证用户（未实现）"""
        # TODO: 实现手机验证码认证逻辑
        raise NotImplementedError("手机验证码认证尚未实现")


class AuthService:
    """认证服务"""

    def __init__(self):
        self.strategies = {
            "email_password": EmailPasswordAuth(),
            "phone_code": PhoneCodeAuth(),
        }

    async def authenticate(
        self, db: AsyncSession, strategy: str = "email_password", **credentials
    ) -> Optional[models.User]:
        """使用指定策略认证用户"""
        auth_strategy = self.strategies.get(strategy)
        if not auth_strategy:
            raise ValueError(f"未知的认证策略: {strategy}")

        return await auth_strategy.authenticate(db, **credentials)


# 创建全局实例
auth_service = AuthService()
