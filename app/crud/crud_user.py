# app/crud/crud_user.py
from datetime import datetime
from typing import Optional, Dict, Any, Union
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, filter_model_fields


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        """通过邮箱获取用户"""
        statement = select(User).where(User.email == email)
        result = await db.execute(statement)
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        """创建新用户，自动处理密码哈希"""
        # 处理密码哈希
        create_data = obj_in.model_dump()
        create_data["hashed_password"] = get_password_hash(create_data.pop("password"))
        create_data["is_superuser"] = False  # 默认不是超级用户

        # 添加时间戳
        now = datetime.now()
        create_data.update({"created_at": now, "updated_at": now})

        # 只保留User模型中存在的字段
        filtered_data = filter_model_fields(User, create_data)
        db_obj = User(**filtered_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: User,
        obj_in: UserUpdate | Dict[str, Any],
    ) -> User:
        """更新用户，自动处理密码哈希"""
        # 处理不同的输入类型
        if isinstance(obj_in, dict):
            update_data = obj_in.copy()
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        # 如果更新密码，需要哈希处理
        if "password" in update_data:
            hashed_password = get_password_hash(update_data.pop("password"))
            update_data["hashed_password"] = hashed_password

        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def authenticate(
        self, db: AsyncSession, *, email: str, password: str
    ) -> Optional[User]:
        """验证用户登录"""
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, str(user.hashed_password)):
            return None
        return user

    async def is_active(self, user: User) -> bool:
        """检查用户是否激活（当前总是返回 True，可根据需求扩展）"""
        return True

    async def is_superuser(self, user: User) -> bool:
        """检查是否为超级用户"""
        return bool(user.is_superuser)


# 创建 CRUD 实例
user = CRUDUser(User)
