from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from enum import Enum


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

    @app.exception_handler(BusinessException)
    async def business_exception_handler(request: Request, exc: BusinessException):
        """处理我们主动抛出的 BusinessException"""
        return JSONResponse(
            status_code=exc.code,
            content={"code": exc.code, "msg": exc.msg, "data": None},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """处理所有其他未捕获的异常"""
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"code": 500, "msg": f"Internal Server Error: {exc}", "data": None},
        )


class BusinessErrorCode(Enum):
    # 系统错误
    SYSTEM_ERROR = (9999, "system error")
    # 用户相关
    USER_ERROR = (1001, "interview already exists")
    # 聊天相关
    CHAT_ERROR = (2002, "chat error")
    # 订单相关
    ORDER_ERROR = (3003, "order error")
    # 可扩展更多业务错误码

    def __init__(self, code, msg):
        self._code = code
        self._msg = msg

    @property
    def code(self):
        return self._code

    @property
    def msg(self):
        return self._msg


class BusinessException(Exception):
    def __init__(
        self,
        error_enum: BusinessErrorCode = BusinessErrorCode.SYSTEM_ERROR,
        msg: str = "",
    ):
        self.code = error_enum.code
        self.msg = msg or error_enum.msg
        super().__init__(self.msg)

    def __str__(self):
        return f"BusinessException(code={self.code}, msg={self.msg})"
