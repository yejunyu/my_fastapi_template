# app/core/config.py
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 项目配置
    PROJECT_NAME: str = "Production-Ready FastAPI"
    PROJECT_VERSION: str = "1.0.0"

    # PostgreSQL 数据库配置
    # 使用 pydantic-settings，它会自动从环境变量中读取
    # 格式: postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DB_NAME
    POSTGRES_USER: str = "root"
    POSTGRES_PASSWORD: str = "123456"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "fastapi"

    # 构造数据库 URL
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Redis 配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # JWT 配置
    SECRET_KEY: str = ""  # 用于签名 JWT 的密钥，必须保密
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # Token 有效期: 8 天

    class Config:
        # 指定 .env 文件的路径
        env_file = ".env"
        # 指定 .env 文件的编码
        env_file_encoding = "utf-8"


settings = Settings()
