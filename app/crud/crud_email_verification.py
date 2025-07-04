from datetime import datetime
from typing import Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.email_verification import EmailVerification, VerificationType
from app.schemas.email_verification import (
    EmailVerificationCreate,
    EmailVerificationUpdate,
)


class CRUDEmailVerification(
    CRUDBase[EmailVerification, EmailVerificationCreate, EmailVerificationUpdate]
):

    async def get_by_token(
        self, db: AsyncSession, *, token: str
    ) -> Optional[EmailVerification]:
        """通过token获取验证记录"""
        statement = select(EmailVerification).where(EmailVerification.token == token)
        result = await db.execute(statement)
        return result.scalars().first()

    async def get_active_token(
        self, db: AsyncSession, *, user_id: int, verification_type: VerificationType
    ) -> Optional[EmailVerification]:
        """获取用户的有效验证token"""
        statement = select(EmailVerification).where(
            and_(
                EmailVerification.user_id == user_id,
                EmailVerification.verification_type == verification_type,
                EmailVerification.is_used == "false",
                EmailVerification.expires_at > datetime.now(),
            )
        )
        result = await db.execute(statement)
        return result.scalars().first()

    async def create_verification_token(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        email: str,
        verification_type: VerificationType,
        expire_hours: int = 2,
    ) -> EmailVerification:
        """创建验证token"""
        # 先使现有的同类型token失效
        await self.invalidate_user_tokens(
            db, user_id=user_id, verification_type=verification_type
        )

        # 创建新的验证token
        verification = EmailVerification.create_token(
            user_id=user_id,
            email=email,
            verification_type=verification_type,
            expire_hours=expire_hours,
        )

        db.add(verification)
        await db.commit()
        await db.refresh(verification)
        return verification

    async def verify_and_use_token(
        self, db: AsyncSession, *, token: str, verification_type: VerificationType
    ) -> Optional[EmailVerification]:
        """验证并使用token"""
        verification = await self.get_by_token(db, token=token)

        if not verification:
            return None

        # 检查token类型
        if verification.verification_type != verification_type:
            return None

        # 检查是否已使用
        if verification.is_used == "true":
            return None

        # 检查是否过期
        if verification.is_expired():
            return None

        # 标记为已使用
        verification.mark_as_used()
        await db.commit()
        await db.refresh(verification)

        return verification

    async def invalidate_user_tokens(
        self, db: AsyncSession, *, user_id: int, verification_type: VerificationType
    ) -> None:
        """使用户的指定类型token失效"""
        statement = select(EmailVerification).where(
            and_(
                EmailVerification.user_id == user_id,
                EmailVerification.verification_type == verification_type,
                EmailVerification.is_used == "false",
            )
        )
        result = await db.execute(statement)
        tokens = result.scalars().all()

        for token in tokens:
            token.mark_as_used()

        await db.commit()

    async def cleanup_expired_tokens(self, db: AsyncSession) -> int:
        """清理过期的token"""
        statement = select(EmailVerification).where(
            EmailVerification.expires_at < datetime.utcnow()
        )
        result = await db.execute(statement)
        expired_tokens = result.scalars().all()

        count = len(expired_tokens)
        for token in expired_tokens:
            await db.delete(token)

        await db.commit()
        return count


# 创建 CRUD 实例
email_verification = CRUDEmailVerification(EmailVerification)
