# app/main.py
from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.api import api_router

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

# 在这里，我们稍后会添加生命周期事件和路由


@app.get("/", tags=["Root"])
async def read_root():
    """
    一个简单的根路径，用于健康检查或欢迎信息。
    """
    return {"message": f"Welcome to {settings.PROJECT_NAME}!"}

app.include_router(api_router, prefix="/api/v1") # <--- 添加
