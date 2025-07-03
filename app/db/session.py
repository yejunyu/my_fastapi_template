# app/db/session.py
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

# 创建异步数据库引擎
# pool_pre_ping=True 会在每次从连接池中获取连接时，先测试其连通性，
# 避免获取到已失效的数据库连接。这是生产环境推荐的配置。
engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)

# 创建一个异步会话工厂
# expire_on_commit=False 防止在提交事务后，访问已提交的对象时出现错误
AsyncSessionFactory = async_sessionmaker(
    engine, autoflush=False, expire_on_commit=False, class_=AsyncSession
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI 依赖项，用于获取数据库会话。
    它确保数据库会话在使用后总是被关闭。
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
        finally:
            await session.close()
