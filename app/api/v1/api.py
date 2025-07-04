# app/api/v1/api.py
from fastapi import APIRouter
from app.api.v1.endpoints import login, todos, demo  # <--- 导入 todos 和 demo

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
# 将 todos 路由包含进来，并设置统一前缀和标签
api_router.include_router(todos.router, prefix="/todos", tags=["todos"])
# 添加演示路由
api_router.include_router(demo.router, prefix="/demo", tags=["demo"])
