# app/core/security.py
from datetime import datetime, timedelta, timezone
from typing import Any


from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# 创建一个 CryptContext 实例，用于密码哈希
# "bcrypt" 是推荐的算法
# deprecated="auto" 会自动处理旧的哈希算法（如果将来需要升级）
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = settings.ALGORITHM


def create_access_token(subject: Any, expires_delta: timedelta | None = None) -> str:
    """
    创建 JWT access token.

    :param subject: token 的主体，通常是用户ID或手机号
    :param expires_delta: token 的有效时间增量
    :return: JWT token 字符串
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # 如果没有提供 expires_delta，使用配置文件中的默认值
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # 构建要编码到 token 中的数据
    to_encode = {"exp": expire, "sub": str(subject)}

    # 使用密钥和算法对数据进行编码
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码是否与哈希密码匹配.

    :param plain_password: 用户输入的明文密码
    :param hashed_password: 数据库中存储的哈希密码
    :return: 如果匹配则返回 True，否则返回 False
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    对明文密码进行哈希处理.

    :param password: 明文密码
    :return: 哈希后的密码字符串
    """
    return pwd_context.hash(password)
