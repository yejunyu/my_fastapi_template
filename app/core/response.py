import json
from fastapi import Request
from fastapi.routing import APIRoute
from fastapi.responses import JSONResponse, Response
from typing import Callable, Any, Coroutine


class UnifiedResponseRoute(APIRoute):
    """统一响应封装路由类，自动将所有响应包装为标准格式"""

    def get_route_handler(
        self,
    ) -> Callable[[Request], Coroutine[Any, Any, JSONResponse]]:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> JSONResponse:
            # 注意：异常处理已经移到专门的处理器中
            # 这里只处理成功的情况
            response = await original_route_handler(request)

            # 检查返回值是否已经是Response对象
            if isinstance(response, Response):
                # 如果是JSONResponse，提取其内容
                if isinstance(response, JSONResponse):
                    try:
                        body = response.body
                        if isinstance(body, (bytes, memoryview)):
                            body_str = bytes(body).decode("utf-8")
                            data = json.loads(body_str)
                        else:
                            data = None
                    except (json.JSONDecodeError, AttributeError, UnicodeDecodeError):
                        data = None
                else:
                    # 其他类型的Response，提取body
                    try:
                        body = response.body if hasattr(response, "body") else None
                        if body and isinstance(body, (bytes, memoryview)):
                            data = bytes(body).decode("utf-8")
                        else:
                            data = None
                    except (AttributeError, UnicodeDecodeError):
                        data = None
            else:
                # 纯数据，直接使用
                if isinstance(response, (bytes, memoryview)):
                    try:
                        data = response.decode("utf-8")
                    except Exception:
                        data = None
                else:
                    data = response

            return JSONResponse(content={"code": 0, "msg": "success", "data": data})

        return custom_route_handler
