from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class InterviewBase(BaseModel):
    task_id: Optional[str] = None
    status: Optional[int] = None
    interview_result: Optional[dict] = None
    extra: Optional[str] = None
    created_at: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[int] = None


class InterviewCreate(InterviewBase):
    pass


class InterviewUpdate(InterviewBase):
    pass


class InterviewOut(InterviewBase):

    class Config:
        from_attributes = True
