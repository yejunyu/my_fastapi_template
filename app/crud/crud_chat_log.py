from app.models.chat_log import ChatLog
from app.schemas import ChatLogCreate, ChatLogUpdate
from app.crud.base import CRUDBase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc
from typing import Sequence


class CRUDChatLog(CRUDBase[ChatLog, ChatLogCreate, ChatLogUpdate]):
    async def get_chat_logs_by_taskid(
        self, db: AsyncSession, task_id: str
    ) -> Sequence[ChatLog]:
        result = await db.execute(
            select(ChatLog)
            .where(ChatLog.task_id == task_id)
            .order_by(asc(ChatLog.created_at))
        )
        return result.scalars().all()


crud_chat_log = CRUDChatLog(ChatLog)
