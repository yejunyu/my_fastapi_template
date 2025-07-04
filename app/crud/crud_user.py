# app/crud/crud_user.py
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_phone(self, db: AsyncSession, *, phone: str) -> Optional[User]:
        """通过手机号获取用户"""
        statement = select(User).where(User.phone == phone)
        result = await db.execute(statement)
        return result.scalars().first()

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
        create_data["is_active"] = False  # 默认未激活，需要邮件验证

        # 添加时间戳
        now = datetime.now()
        create_data.update({"created_at": now, "updated_at": now})

        db_obj = User(**create_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: User, obj_in: UserUpdate
    ) -> User:
        """更新用户，自动处理密码哈希"""
        update_data = obj_in.model_dump(exclude_unset=True)

        # 如果更新密码，需要哈希处理
        if "password" in update_data:
            hashed_password = get_password_hash(update_data.pop("password"))
            update_data["hashed_password"] = hashed_password

        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def authenticate(
        self, db: AsyncSession, *, phone: str, password: str
    ) -> Optional[User]:
        """验证用户登录（手机号方式，保留兼容性）"""
        user = await self.get_by_phone(db, phone=phone)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def authenticate_by_email(
        self, db: AsyncSession, *, email: str, password: str
    ) -> Optional[User]:
        """验证用户登录（邮箱方式）"""
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        # 检查账户是否已激活
        if not user.is_active:
            return None
        return user

    async def activate_user(self, db: AsyncSession, *, user: User) -> User:
        """激活用户账户"""
        user.is_active = True
        await db.commit()
        await db.refresh(user)
        return user

    async def update_password(
        self, db: AsyncSession, *, user: User, new_password: str
    ) -> User:
        """更新用户密码"""
        user.hashed_password = get_password_hash(new_password)
        await db.commit()
        await db.refresh(user)
        return user

    async def is_active(self, user: User) -> bool:
        """检查用户是否激活"""
        return user.is_active

    async def is_superuser(self, user: User) -> bool:
        """检查是否为超级用户"""
        return user.is_superuser


# 创建 CRUD 实例
user = CRUDUser(User)
