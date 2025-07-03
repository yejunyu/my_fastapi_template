from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException


def setup_exception_handlers(app: FastAPI) -> None:
    """注册所有异常处理器到FastAPI应用"""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        """处理 Pydantic 验证错误"""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "code": 422,
                "msg": "Validation Error: " + str(exc.errors()[0]["msg"]),
                "data": exc.errors(),
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """处理我们主动抛出的 HTTPException"""
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.status_code, "msg": exc.detail, "data": None},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """处理所有其他未捕获的异常"""
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"code": 500, "msg": f"Internal Server Error: {exc}", "data": None},
        )
