from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
from loguru import logger

from app.core.response import UnifiedResponseRoute
from app.core.exceptions import setup_exception_handlers
from app.core.middleware import setup_middlewares
from app.api.v1.api import api_router

# 配置 loguru 日志
import sys

logger.remove()  # 移除默认处理器
logger.add(
    sink=sys.stdout,  # 输出到控制台
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
)

# --- FastAPI App 初始化 ---
app = FastAPI(title="My FastAPI Template", version="1.0.0")

# 应用统一响应封装
app.router.route_class = UnifiedResponseRoute

# 注册异常处理器
setup_exception_handlers(app)

# 注册中间件
setup_middlewares(app)

app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
