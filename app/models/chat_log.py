from sqlalchemy import Column, Integer, String, Boolean
from .base import BaseModel


class ChatLog(BaseModel):
    __tablename__ = "chat_log"
    user_id = Column(String(255), nullable=False, comment="用户ID")
    task_id = Column(String(255), nullable=False, comment="任务ID")
    message = Column(String(1024), nullable=False, comment="消息")
    is_ai = Column(Boolean, nullable=False, comment="是否是AI消息")
