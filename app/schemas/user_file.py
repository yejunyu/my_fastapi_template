from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserFileBase(BaseModel):
    filename: str
    file_path: str
    file_type: str
    text_content: str
    user_id: Optional[int] = None
    job_intention: Optional[str] = None
    resume_experience: Optional[str] = None


class UserFileCreate(UserFileBase):
    pass


class UserFileUpdate(BaseModel):
    text_content: Optional[str] = None
    job_intention: Optional[str] = None
    resume_experience: Optional[str] = None


class UserFileInDB(UserFileBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class UserFilePublic(UserFileInDB):
    pass
