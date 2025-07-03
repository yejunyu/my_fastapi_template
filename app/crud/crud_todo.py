# app/crud/crud_todo.py
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.crud.base import CRUDBase
from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate


class CRUDTodo(CRUDBase[Todo, TodoCreate, TodoUpdate]):
    async def create_with_owner(
        self, db: AsyncSession, *, obj_in: TodoCreate, owner_id: int
    ) -> Todo:
        """创建 todo 项目，指定所有者"""
        create_data = obj_in.model_dump()
        create_data["owner_id"] = owner_id

        # 添加时间戳
        now = datetime.now()
        create_data.update({"created_at": now, "updated_at": now})

        db_obj = Todo(**create_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_owner(
        self, db: AsyncSession, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Todo]:
        """获取指定用户的所有 todo 项目"""
        statement = (
            select(Todo).where(Todo.owner_id == owner_id).offset(skip).limit(limit)
        )
        result = await db.execute(statement)
        return list(result.scalars().all())

    async def get_by_owner_and_id(
        self, db: AsyncSession, *, id: int, owner_id: int
    ) -> Optional[Todo]:
        """获取指定用户的特定 todo 项目"""
        statement = select(Todo).where(Todo.id == id, Todo.owner_id == owner_id)
        result = await db.execute(statement)
        return result.scalars().first()

    async def count_by_owner(self, db: AsyncSession, *, owner_id: int) -> int:
        """统计指定用户的 todo 项目数量"""
        from sqlalchemy import func

        statement = select(func.count(Todo.id)).where(Todo.owner_id == owner_id)
        result = await db.execute(statement)
        return result.scalar() or 0

    async def get_completed_by_owner(
        self, db: AsyncSession, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Todo]:
        """获取指定用户已完成的 todo 项目"""
        statement = (
            select(Todo)
            .where(Todo.owner_id == owner_id, Todo.is_completed == True)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return list(result.scalars().all())

    async def get_pending_by_owner(
        self, db: AsyncSession, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Todo]:
        """获取指定用户未完成的 todo 项目"""
        statement = (
            select(Todo)
            .where(Todo.owner_id == owner_id, Todo.is_completed == False)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return list(result.scalars().all())


# 创建 CRUD 实例
todo = CRUDTodo(Todo)
