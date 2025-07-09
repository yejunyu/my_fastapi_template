from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class InterviewInfo(BaseModel):
    job_intention: str
    resume_experience: str
    task_id: str


class InterviewInfoUpdate(BaseModel):
    job_intention: Optional[str] = None
    resume_experience: Optional[str] = None


class VoiceChatIn(BaseModel):
    request: str | None = None
    task_id: str


class ChatLogCreate(BaseModel):
    user_id: str
    task_id: str
    message: str
    is_ai: bool


class ChatLogUpdate(BaseModel):
    user_id: Optional[str] = None
    task_id: Optional[str] = None
    message: Optional[str] = None
    is_ai: Optional[bool] = None


class ChatLogOut(BaseModel):
    id: int
    user_id: str
    task_id: str
    message: str
    is_ai: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
