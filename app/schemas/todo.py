# app/schemas/todo.py
from typing import Optional
from pydantic import BaseModel


# 共享的基础属性
class TodoBase(BaseModel):
    content: str
    is_completed: bool = False


# 用于创建 todo 项目的模型 (从客户端接收)
class TodoCreate(TodoBase):
    pass


# 更新时可以从客户端接收的属性 (所有字段都可选)
class TodoUpdate(BaseModel):
    content: Optional[str] = None
    is_completed: Optional[bool] = None


# 用于从 API 返回 todo 项目的模型，包含数据库字段
class TodoPublic(TodoBase):
    id: int
    owner_id: int
