# app/api/v1/endpoints/todos.py
from typing import List, cast
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, models, schemas
from app.api import deps

router = APIRouter(prefix="/todos", tags=["待办事项"])


@router.post("/", response_model=schemas.TodoPublic)
async def create_new_todo(
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    todo_in: schemas.TodoCreate,
    current_user: models.User = Depends(deps.get_current_user),
) -> models.Todo:
    """
    创建新的待办事项。
    """
    todo = await crud.todo.create_with_owner(
        db_session, obj_in=todo_in, owner_id=cast(int, current_user.id)
    )
    return todo


@router.get("/", response_model=List[schemas.TodoPublic])
async def read_user_todos(
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_user),
) -> List[models.Todo]:
    """
    获取当前用户的所有待办事项。
    """
    todos = await crud.todo.get_by_owner(
        db_session, owner_id=cast(int, current_user.id), skip=skip, limit=limit
    )
    return todos


@router.put("/{id}", response_model=schemas.TodoPublic)
async def update_user_todo(
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    id: int,
    todo_in: schemas.TodoUpdate,
    current_user: models.User = Depends(deps.get_current_user),
) -> models.Todo:
    """
    更新一个待办事项。
    """
    db_todo = await crud.todo.get_by_owner_and_id(
        db_session, id=id, owner_id=cast(int, current_user.id)
    )
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo = await crud.todo.update(db_session, db_obj=db_todo, obj_in=todo_in)
    return todo


@router.delete("/{id}", response_model=schemas.Msg)
async def delete_user_todo(
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> schemas.Msg:
    """
    删除一个待办事项。
    """
    db_todo = await crud.todo.get_by_owner_and_id(
        db_session, id=id, owner_id=cast(int, current_user.id)
    )
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    await crud.todo.remove(db_session, id=id)
    return schemas.Msg(msg="Todo deleted successfully")
