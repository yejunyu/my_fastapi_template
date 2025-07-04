from datetime import datetime
from typing import Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.email_verification import EmailVerificationCode


class CRUDEmailVerification:
    async def create_code(
        self, db: AsyncSession, *, email: str, code: str, valid_minutes: int = 10
    ) -> EmailVerificationCode:
        """创建验证码"""
        db_obj = EmailVerificationCode.create_code(email, code, valid_minutes)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_valid_code(
        self, db: AsyncSession, *, email: str, code: str
    ) -> Optional[EmailVerificationCode]:
        """获取有效的验证码"""
        statement = (
            select(EmailVerificationCode)
            .where(
                and_(  # type: ignore
                    EmailVerificationCode.email == email,
                    EmailVerificationCode.code == code,
                    EmailVerificationCode.used == False,  # type: ignore
                    EmailVerificationCode.expires_at > datetime.now(),
                )
            )
            .order_by(EmailVerificationCode.created_at.desc())
        )

        result = await db.execute(statement)
        return result.scalars().first()

    async def mark_as_used(
        self, db: AsyncSession, *, code_obj: EmailVerificationCode
    ) -> EmailVerificationCode:
        """标记验证码为已使用"""
        code_obj.mark_as_used()
        await db.commit()
        await db.refresh(code_obj)
        return code_obj

    async def cleanup_expired(self, db: AsyncSession) -> int:
        """清理过期的验证码"""
        from sqlalchemy import delete

        statement = delete(EmailVerificationCode).where(
            EmailVerificationCode.expires_at <= datetime.utcnow()
        )
        result = await db.execute(statement)
        await db.commit()
        return result.rowcount  # type: ignore


# 创建 CRUD 实例
email_verification = CRUDEmailVerification()
