from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from .base import Base, BaseModel


class UserFile(BaseModel):
    __tablename__ = "user_file"
    filename = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)
    text_content = Column(Text, nullable=True)
    user_id = Column(Integer, nullable=False)
    job_intention = Column(String(255), nullable=True)
    resume_experience = Column(Text, nullable=True)
