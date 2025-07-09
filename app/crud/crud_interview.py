from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.interview import Interview, InterviewStatus
from app.schemas.interview import InterviewCreate, InterviewUpdate, InterviewOut
from app.crud.base import CRUDBase


class CRUDInterview(CRUDBase[Interview, InterviewCreate, InterviewUpdate]):
    async def get_by_task_id(
        self, db: AsyncSession, task_id: str, uid: int
    ) -> Optional[Interview]:
        result = await db.execute(
            select(Interview).where(
                Interview.task_id == task_id, Interview.user_id == uid
            )
        )
        return result.scalars().first()

    async def get_interviewing(self, db: AsyncSession) -> Sequence[Interview]:
        result = await db.execute(
            select(Interview).where(Interview.status == InterviewStatus.START_INTERVIEW)
        )
        return result.scalars().all()

    async def get_interviewing_by_uid(
        self, db: AsyncSession, uid: int
    ) -> Optional[Interview]:
        result = await db.execute(
            select(Interview)
            .where(
                Interview.user_id == uid,
                Interview.status == InterviewStatus.START_INTERVIEW,
            )
            .order_by(Interview.updated_at.desc())
        )
        return result.scalars().first()

    async def get_interview_result_by_uid(
        self, db: AsyncSession, uid: int
    ) -> Sequence[Interview]:
        result = await db.execute(
            select(Interview)
            .filter(
                Interview.user_id == uid,
                Interview.status != InterviewStatus.START_INTERVIEW,
            )
            .order_by(Interview.updated_at.desc())
        )
        return result.scalars().all()

    async def get_multi_by_status(
        self, db: AsyncSession, status: int, skip: int = 0, limit: int = 100
    ) -> Sequence[Interview]:
        result = await db.execute(
            select(Interview)
            .where(Interview.status == status)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def update_updated_at_by_uid_taskid(
        self, db: AsyncSession, user_id: int, task_id: str
    ) -> int:
        result = await db.execute(
            select(Interview).where(
                Interview.user_id == user_id, Interview.task_id == task_id
            )
        )
        interview = result.scalars().first()
        if interview:
            from datetime import datetime, timezone

            setattr(interview, "updated_at", datetime.now(timezone.utc))
            db.add(interview)
            await db.commit()
            await db.refresh(interview)
            return 1
        return 0

    async def end_interview(
        self,
        db: AsyncSession,
        interview: Interview,
        status: InterviewStatus = InterviewStatus.INTERVIEW_COMPLETED,
        extra_msg: str = "",
    ) -> Interview:
        """
        结束面试，更新状态、结束时间和时长
        """
        from datetime import datetime, timezone

        # 设置结束时间
        setattr(interview, "end_time", datetime.now(timezone.utc))

        # 计算时长（秒）
        if hasattr(interview, "created_at") and getattr(interview, "created_at", None):
            duration = int((interview.end_time - interview.created_at).total_seconds())
            setattr(interview, "duration", duration)

        # 设置状态
        setattr(interview, "status", status.value)

        if extra_msg:
            setattr(interview, "extra", extra_msg)

        # 保存到数据库
        db.add(interview)
        await db.commit()
        await db.refresh(interview)

        return interview


crud_interview = CRUDInterview(Interview)
