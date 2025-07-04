# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.config import settings
from app.api.v1.api import api_router
from app.middleware.simple_wrapper import SimpleResponseWrapperMiddleware
from app.middleware.exception_handler import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
    starlette_http_exception_handler,
)

# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="ai面试助手",
    # 在生产环境中可以禁用 OpenAPI (Swagger UI) 和 ReDoc
    # openapi_url="/api/v1/openapi.json",
    # docs_url=None,
    # redoc_url=None
)

# 添加异常处理器
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 添加响应格式统一化中间件
app.add_middleware(
    SimpleResponseWrapperMiddleware,
    skip_paths=["/", "/health", "/test-simple", "/docs", "/redoc", "/openapi.json"],
)

# 在这里，我们稍后会添加生命周期事件和路由


@app.get("/", tags=["Root"])
async def read_root():
    """
    一个简单的根路径，用于健康检查或欢迎信息。
    """
    return {"message": f"Welcome to {settings.PROJECT_NAME}!"}


@app.get("/health", tags=["Health"])
async def health_check():
    """
    健康检查端点，不使用统一响应格式
    """
    return {"status": "healthy", "service": settings.PROJECT_NAME}


@app.get("/test-simple", tags=["Test"])
async def test_simple():
    """
    简单测试端点，不经过中间件包装
    """
    return {"message": "Simple test without middleware", "code": 200}


@app.get("/test-wrapped", tags=["Test"])
async def test_wrapped():
    """
    测试端点，会经过中间件包装
    """
    return {"message": "This should be wrapped", "original_data": True}


app.include_router(api_router, prefix="/api/v1")  # <--- 添加
