from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.password_reset import PasswordReset


class CRUDPasswordReset:
    async def create_token(
        self, db: AsyncSession, *, user_id: int, valid_minutes: int = 30
    ) -> PasswordReset:
        """创建密码重置token"""
        db_obj = PasswordReset.create_token(user_id, valid_minutes)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_valid_token(
        self, db: AsyncSession, *, token: str
    ) -> Optional[PasswordReset]:
        """获取有效的重置token"""
        statement = select(PasswordReset).where(
            and_(  # type: ignore
                PasswordReset.token == token,
                PasswordReset.used == False,  # type: ignore
                PasswordReset.expires_at > datetime.now(timezone.utc),
            )
        )

        result = await db.execute(statement)
        return result.scalars().first()

    async def mark_as_used(
        self, db: AsyncSession, *, token_obj: PasswordReset
    ) -> PasswordReset:
        """标记token为已使用"""
        token_obj.mark_as_used()
        await db.commit()
        await db.refresh(token_obj)
        return token_obj

    async def cleanup_expired(self, db: AsyncSession) -> int:
        """清理过期的token"""
        from sqlalchemy import delete

        statement = delete(PasswordReset).where(
            PasswordReset.expires_at <= datetime.now(timezone.utc)
        )
        result = await db.execute(statement)
        await db.commit()
        return result.rowcount  # type: ignore


# 创建 CRUD 实例
password_reset = CRUDPasswordReset()
