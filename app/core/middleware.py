import time
from fastapi import FastAPI, Request
from loguru import logger


def setup_middlewares(app: FastAPI) -> None:
    """注册所有中间件到FastAPI应用"""

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """请求日志记录中间件"""
        start_time = time.time()

        # 执行请求
        response = await call_next(request)

        process_time = (time.time() - start_time) * 1000
        formatted_process_time = f"{process_time:.2f}ms"

        logger.info(
            f"Request: {request.method} {request.url.path} | "
            f"Status: {response.status_code} | "
            f"Duration: {formatted_process_time}"
        )

        return response
