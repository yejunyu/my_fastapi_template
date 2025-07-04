# app/api/v1/endpoints/demo.py
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, RedirectResponse
from typing import Optional
from pydantic import BaseModel

router = APIRouter()


class DemoData(BaseModel):
    id: int
    name: str
    description: Optional[str] = None


@router.get("/success")
async def demo_success():
    """
    演示成功响应
    返回格式: {code: 0, msg: "success", data: {...}}
    """
    return {"id": 1, "name": "演示数据", "description": "这是一个成功的响应示例"}


@router.get("/success-list")
async def demo_success_list():
    """
    演示成功响应（列表）
    """
    return [
        {"id": 1, "name": "项目1"},
        {"id": 2, "name": "项目2"},
        {"id": 3, "name": "项目3"},
    ]


@router.get("/error-400")
async def demo_error_400():
    """
    演示400错误
    返回格式: {code: 400, msg: "Bad request", data: null}
    """
    raise HTTPException(status_code=400, detail="这是一个400错误示例")


@router.get("/error-404")
async def demo_error_404():
    """
    演示404错误
    """
    raise HTTPException(status_code=404, detail="资源未找到")


@router.get("/error-500")
async def demo_error_500():
    """
    演示500错误（未捕获异常）
    """
    # 故意抛出一个未捕获的异常
    raise ValueError("这是一个未捕获的异常示例")


@router.post("/validation-error")
async def demo_validation_error(data: DemoData):
    """
    演示参数验证错误
    返回格式: {code: 422, msg: "field -> name: field required", data: [...]}
    """
    return {"message": "数据验证成功", "data": data}


@router.get("/query-validation")
async def demo_query_validation(
    page: int = Query(..., ge=1, description="页码，必须大于等于1"),
    size: int = Query(10, ge=1, le=100, description="每页大小，1-100之间"),
):
    """
    演示查询参数验证错误
    """
    return {"page": page, "size": size, "message": "查询参数验证成功"}


@router.get("/file-download")
async def demo_file_download():
    """
    演示文件下载（不会被中间件包装）
    """
    # 注意：这只是演示，实际文件可能不存在
    return FileResponse(path="app/main.py", filename="demo.py", media_type="text/plain")


@router.get("/redirect")
async def demo_redirect():
    """
    演示重定向（不会被中间件包装）
    """
    return RedirectResponse(url="/api/v1/demo/success")


@router.get("/custom-message")
async def demo_custom_message():
    """
    演示自定义消息的成功响应
    """
    return {
        "status": "completed",
        "result": "操作成功完成",
        "timestamp": "2024-01-15T10:30:00Z",
    }
