from typing import Optional
from pydantic import BaseModel


class InterviewInfo(BaseModel):
    job_intention: str
    resume_experience: str
    task_id: str


class InterviewInfoUpdate(BaseModel):
    job_intention: Optional[str] = None
    resume_experience: Optional[str] = None


class VoiceChatIn(BaseModel):
    request: str
