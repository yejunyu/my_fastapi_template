from sqlalchemy import Column, Integer, String, Text
from .base import BaseModel


class UserFile(BaseModel):
    __tablename__ = "user_file"
    filename = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)
    text_content = Column(Text, nullable=True)
    user_id = Column(Integer, nullable=False)
    task_id = Column(String(255), nullable=False, default="123")
    job_intention = Column(Text, nullable=True)
    resume_experience = Column(Text, nullable=True)
