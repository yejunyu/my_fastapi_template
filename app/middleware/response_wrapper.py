# app/middleware/response_wrapper.py
import logging
from typing import Any, List, Optional
from fastapi import Request, Response
from fastapi.responses import (
    JSONResponse,
    FileResponse,
    RedirectResponse,
    StreamingResponse,
    HTMLResponse,
)
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse
import time

logger = logging.getLogger(__name__)


class ResponseWrapperMiddleware(BaseHTTPMiddleware):
    """
    响应格式统一化中间件
    将所有API响应包装为 {code: int, msg: str, data: any} 格式
    """

    def __init__(
        self,
        app,
        skip_paths: Optional[List[str]] = None,
        skip_prefixes: Optional[List[str]] = None,
        success_code: int = 0,
        success_msg: str = "success",
    ):
        """
        初始化中间件

        Args:
            app: FastAPI应用实例
            skip_paths: 跳过包装的完整路径列表
            skip_prefixes: 跳过包装的路径前缀列表
            success_code: 成功时的业务码
            success_msg: 成功时的消息
        """
        super().__init__(app)
        self.skip_paths = skip_paths or []
        self.skip_prefixes = skip_prefixes or [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/static",
        ]
        self.success_code = success_code
        self.success_msg = success_msg

    def should_skip_wrapping(self, request: Request) -> bool:
        """判断是否应该跳过响应包装"""
        path = request.url.path

        # 检查完整路径
        if path in self.skip_paths:
            return True

        # 检查路径前缀
        for prefix in self.skip_prefixes:
            if path.startswith(prefix):
                return True

        return False

    def is_special_response(self, response: StarletteResponse) -> bool:
        """判断是否为特殊响应类型（不需要包装）"""
        special_types = (
            FileResponse,
            RedirectResponse,
            StreamingResponse,
            HTMLResponse,
        )
        return isinstance(response, special_types)

    async def dispatch(self, request: Request, call_next) -> Response:
        """中间件主要逻辑"""
        start_time = time.perf_counter()

        try:
            # 检查是否跳过此路径
            if self.should_skip_wrapping(request):
                response = await call_next(request)
                return response

            # 执行请求
            response = await call_next(request)

            # 处理响应时间
            process_time = time.perf_counter() - start_time

            # 检查是否为特殊响应类型
            if self.is_special_response(response):
                response.headers["X-Process-Time"] = str(process_time)
                return response

            # 包装响应
            wrapped_response = await self.wrap_response(response, process_time)
            return wrapped_response

        except Exception as e:
            # 处理未捕获的异常
            logger.error(f"Response wrapper middleware error: {str(e)}", exc_info=True)
            process_time = time.perf_counter() - start_time

            return self.create_error_response(
                code=500, msg="Internal server error", process_time=process_time
            )

    async def wrap_response(
        self, response: StarletteResponse, process_time: float
    ) -> JSONResponse:
        """包装响应为统一格式"""
        try:
            # 确定业务状态码和消息
            if 200 <= response.status_code < 300:
                business_code = self.success_code
                message = self.success_msg
            else:
                business_code = response.status_code
                message = self.get_error_message(response.status_code)

            # 提取响应体数据
            response_data = await self.safe_extract_response_data(response)

            # 构建统一格式
            wrapped_data = {
                "code": business_code,
                "msg": message,
                "data": response_data,
            }

            # 创建新的JSONResponse
            new_response = JSONResponse(
                content=wrapped_data,
                status_code=200,  # 统一返回200，业务状态通过code字段表示
                headers=dict(response.headers) if hasattr(response, "headers") else {},
            )

            # 添加处理时间头
            new_response.headers["X-Process-Time"] = str(process_time)

            return new_response

        except Exception as e:
            logger.error(f"Failed to wrap response: {str(e)}", exc_info=True)
            return self.create_error_response(
                code=500, msg="Response processing error", process_time=process_time
            )

    async def safe_extract_response_data(self, response: StarletteResponse) -> Any:
        """安全地提取响应数据，避免消耗响应流"""
        try:
            # 暂时简化逻辑，返回一个标识
            # TODO: 改进响应数据提取逻辑
            return {
                "middleware_processed": True,
                "response_type": type(response).__name__,
            }

        except Exception as e:
            logger.warning(f"Failed to extract response data safely: {str(e)}")
            return {"error": "Failed to extract data"}

    def get_error_message(self, status_code: int) -> str:
        """根据HTTP状态码获取错误消息"""
        error_messages = {
            400: "Bad request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not found",
            405: "Method not allowed",
            422: "Validation error",
            429: "Too many requests",
            500: "Internal server error",
            502: "Bad gateway",
            503: "Service unavailable",
            504: "Gateway timeout",
        }
        return error_messages.get(status_code, f"HTTP {status_code}")

    def create_error_response(
        self,
        code: int,
        msg: str,
        data: Any = None,
        process_time: Optional[float] = None,
    ) -> JSONResponse:
        """创建错误响应"""
        wrapped_data = {"code": code, "msg": msg, "data": data}

        response = JSONResponse(
            content=wrapped_data,
            status_code=200,  # 统一返回200，业务状态通过code字段表示
        )

        if process_time is not None:
            response.headers["X-Process-Time"] = str(process_time)

        return response
