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
        # if str(user.status) != models.UserStatus.ACTIVE.value:
        # return None

        return user


class PhoneCodeAuth(AuthenticationStrategy):
    """手机验证码认证策略（预留）"""

    async def authenticate(
        self, db: AsyncSession, **credentials
    ) -> Optional[models.User]:
        """通过手机号和验证码认证用户（未实现）"""
        # TODO: 实现手机验证码认证逻辑
        raise NotImplementedError("手机验证码认证尚未实现")


class EmailCodeAuth(AuthenticationStrategy):
    """邮箱验证码认证策略"""

    async def authenticate(
        self, db: AsyncSession, **credentials
    ) -> Optional[models.User]:
        """通过邮箱和验证码认证用户"""
        email = credentials.get("email")
        code = credentials.get("password")  # 兼容form表单字段名
        if not email or not code:
            return None
        from app.crud import email_verification, user

        # 校验验证码有效性
        code_obj = await email_verification.get_valid_code(db, email=email, code=code)
        if not code_obj:
            return None
        # 标记验证码为已用
        await email_verification.mark_as_used(db, code_obj=code_obj)
        # 获取用户
        user_obj = await user.get_by_email(db, email=email)
        if not user_obj:
            return None
        # 检查用户状态
        if user_obj.is_active is False:
            return None
        return user_obj


class AuthService:
    """认证服务"""

    def __init__(self):
        self.strategies = {
            "password": EmailPasswordAuth(),
            "phone_code": PhoneCodeAuth(),
            "email_code": EmailCodeAuth(),
        }

    async def authenticate(
        self, db: AsyncSession, strategy: str = "password", **credentials
    ) -> Optional[models.User]:
        """使用指定策略认证用户"""
        auth_strategy: AuthenticationStrategy | None = self.strategies.get(strategy)
        if not auth_strategy:
            raise ValueError(f"未知的认证策略: {strategy}")

        return await auth_strategy.authenticate(db, **credentials)


# 创建全局实例
auth_service = AuthService()
