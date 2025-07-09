# app/api/deps.py
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBasicCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
)
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.core import security
from app.core.exceptions import BusinessException, BusinessErrorCode
from app.core.config import settings
from app.db.session import AsyncSessionFactory

# 创建一个 OAuth2PasswordBearer 实例
# tokenUrl 指向我们获取 token 的接口路径
# reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"/api/v1/users/login")
reusable_oauth2 = HTTPBearer()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI 依赖项，用于获取数据库会话。
    """
    async with AsyncSessionFactory() as session:
        yield session


async def get_current_user(
    db_session: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(reusable_oauth2),
) -> models.User:
    """
    依赖项：获取当前用户。
    - 验证 JWT token
    - 从 token 中解析出用户邮箱
    - 从数据库中获取用户
    """
    token = credentials.credentials  # 获取 token 字符串
    try:
        # 解码 JWT，获取 payload
        payload = jwt.decode(
            token, settings.HUOSHAN_SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        # 从 payload 中获取邮箱
        token_data = schemas.TokenPayload(**payload)
    except (JWTError, ValueError):
        # 如果解码失败或 token 无效，抛出异常
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    # 检查 token_data.sub 是否为 None
    if token_data.sub is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token: missing subject",
        )
    # 使用 token 中的邮箱从数据库中查找用户
    user: models.User = await crud.user.get(db_session, id=int(token_data.sub))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_current_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    依赖项：获取当前用户，并检查是否为超级用户。
    """
    if not bool(current_user.is_superuser):
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user


def require_points(required_points: int):
    """工厂函数，创建需要特定积分的依赖项"""

    async def check_user_points(
        current_user: models.User = Depends(get_current_user),
    ) -> models.User:
        user_points = getattr(current_user, "points", 0)
        if user_points < required_points:
            raise BusinessException(
                error_enum=BusinessErrorCode.POINTS_NOT_ENOUGH,
                msg=f"积分不足，需要{required_points}积分，当前仅有{user_points}积分",
            )
        return current_user

    return check_user_points
