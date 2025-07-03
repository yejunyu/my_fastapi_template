# app/services/user_admin.py
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app import crud, models, schemas
from app.core.security import get_password_hash
from app.models.user import UserStatus


class UserAdminService:
    """用户管理服务"""

    async def create_superuser(
        self, db: AsyncSession, email: str, password: str
    ) -> models.User:
        """创建超级用户"""

        # 检查用户是否已存在
        existing_user = await crud.user.get_by_email(db, email=email)
        if existing_user:
            logger.warning(f"超级用户 {email} 已存在")
            return existing_user

        # 创建超级用户
        user_data = {
            "email": email,
            "hashed_password": get_password_hash(password),
            "status": UserStatus.ACTIVE,
            "is_superuser": True,
        }

        user = models.User(**user_data)
        db.add(user)
        await db.commit()
        await db.refresh(user)

        logger.success(f"超级用户 {email} 创建成功")
        return user

    async def get_user_stats(self, db: AsyncSession) -> dict:
        """获取用户统计信息"""
        from sqlalchemy import func, select

        # 总用户数
        total_users = await db.execute(select(func.count(models.User.id)))
        total_count = total_users.scalar()

        # 激活用户数
        active_users = await db.execute(
            select(func.count(models.User.id)).where(
                models.User.status == UserStatus.ACTIVE
            )
        )
        active_count = active_users.scalar()

        # 超级用户数
        super_users = await db.execute(
            select(func.count(models.User.id)).where(models.User.is_superuser == True)
        )
        super_count = super_users.scalar()

        return {
            "total_users": total_count,
            "active_users": active_count,
            "super_users": super_count,
        }


# 创建全局实例
user_admin_service = UserAdminService()
