import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
from loguru import logger
from sqlalchemy import false, select
from app.db.session import AsyncSessionFactory  # 你的 async_session 工厂

from app.core.response import UnifiedResponseRoute
from app.core.exceptions import setup_exception_handlers
from app.core.middleware import setup_middlewares
from app.api.v1.api import api_router
from fastapi.middleware.cors import CORSMiddleware

# 配置 loguru 日志
import sys

from app.models.interview import Interview

logger.remove()  # 移除默认处理器
logger.add(
    sink=sys.stdout,  # 输出到控制台
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
)

# --- FastAPI App 初始化 ---
app = FastAPI(title="My Interview AI Teacher", version="1.0.0")


async def scan_interview_table():
    while True:
        async with AsyncSessionFactory() as session:
            result = await session.execute(
                select(Interview).where(Interview.status == 0)
                # 可加 where 条件，如 .where(Interview.status == 0)
            )
            interviews = result.scalars().all()
            print(f"定时扫描到 {len(interviews)} 条 interview 记录")
            # 这里可以加你的业务处理逻辑
        await asyncio.sleep(60)  # 每60秒执行一次


@asynccontextmanager
async def lifespan(app):
    # 启动定时任务
    asyncio.create_task(scan_interview_table())
    yield
    # 可选：在此处做清理工作


# 应用统一响应封装
app.router.route_class = UnifiedResponseRoute

# 注册异常处理器
setup_exception_handlers(app)

# 注册中间件
setup_middlewares(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
a