# app/middleware/simple_wrapper.py
import json
import time
from typing import Any, List, Optional
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class SimpleResponseWrapperMiddleware(BaseHTTPMiddleware):
    """
    简化的响应格式统一化中间件
    """

    def __init__(self, app, skip_paths: Optional[List[str]] = None):
        super().__init__(app)
        self.skip_paths = skip_paths or [
            "/",
            "/health",
            "/test-simple",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]

    def should_skip(self, request: Request) -> bool:
        """判断是否跳过处理"""
        path = request.url.path
        return path in self.skip_paths

    async def dispatch(self, request: Request, call_next):
        """中间件主要逻辑"""
        start_time = time.perf_counter()
        path = request.url.path
        print(f"Middleware processing path: {path}")

        # 检查是否跳过
        if self.should_skip(request):
            print(f"Skipping path: {path}")
            return await call_next(request)

        try:
            # 执行请求
            response = await call_next(request)
            process_time = time.perf_counter() - start_time

            # 简单包装 - 返回固定格式
            wrapped_data = {
                "code": 0,
                "msg": "success",
                "data": {
                    "message": "Middleware is working!",
                    "process_time": process_time,
                    "original_status": response.status_code,
                },
            }

            # 创建新响应
            new_response = JSONResponse(content=wrapped_data, status_code=200)
            new_response.headers["X-Process-Time"] = str(process_time)

            return new_response

        except Exception as e:
            # 错误处理
            return JSONResponse(
                content={"code": 500, "msg": f"Error: {str(e)}", "data": None},
                status_code=200,
            )
