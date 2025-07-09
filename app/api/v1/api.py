# app/api/v1/api.py
from fastapi import APIRouter
from app.api.v1.endpoints import chat, login, payment, rtc, todos  # <--- 导入 todos

api_router = APIRouter()
api_router.include_router(login.router)
# 将 todos 路由包含进来，并设置统一前缀和标签
# api_router.include_router(todos.router)
api_router.include_router(chat.router)
api_router.include_router(rtc.router)
api_router.include_router(payment.router)
