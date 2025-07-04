# app/middleware/exception_handler.py
import logging
from typing import Union
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback

logger = logging.getLogger(__name__)


def create_error_response(
    code: int,
    msg: str,
    data: Union[dict, list, str, None] = None,
    request: Request = None,
) -> JSONResponse:
    """创建统一的错误响应"""
    response_data = {"code": code, "msg": msg, "data": data}

    return JSONResponse(
        status_code=200, content=response_data  # 统一返回200，业务状态通过code字段表示
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """处理HTTP异常"""
    logger.warning(
        f"HTTP Exception: {exc.status_code} - {exc.detail} - Path: {request.url.path}"
    )

    return create_error_response(
        code=exc.status_code, msg=str(exc.detail), request=request
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """处理请求验证异常"""
    logger.warning(f"Validation Error: {exc.errors()} - Path: {request.url.path}")

    # 格式化验证错误信息
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")

    error_msg = "; ".join(errors) if errors else "Validation error"

    return create_error_response(
        code=422, msg=error_msg, data=exc.errors(), request=request
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理通用异常"""
    logger.error(f"Unhandled Exception: {str(exc)} - Path: {request.url.path}")
    logger.error(traceback.format_exc())

    return create_error_response(code=500, msg="Internal server error", request=request)


async def starlette_http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """处理Starlette HTTP异常"""
    logger.warning(
        f"Starlette HTTP Exception: {exc.status_code} - {exc.detail} - Path: {request.url.path}"
    )

    return create_error_response(
        code=exc.status_code, msg=str(exc.detail), request=request
    )
