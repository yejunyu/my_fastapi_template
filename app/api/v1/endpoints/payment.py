from typing import List, cast
from fastapi import APIRouter, Depends, HTTPException
from app.core.response import UnifiedResponseRoute

from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, models, schemas
from app.api import deps

router = APIRouter(
    prefix="/payment", tags=["支付相关"], route_class=UnifiedResponseRoute
)


@router.get("/list/props", response_model=schemas.TodoPublic)
async def list_props(
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    todo_in: schemas.TodoCreate,
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    获取商品的列表
    """
    todo = await crud.todo.create_with_owner(
        db_session, obj_in=todo_in, owner_id=cast(int, current_user.id)
    )
    return todo
