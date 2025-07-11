from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class InterviewBase(BaseModel):
    task_id: Optional[str] = None
    # 0: 上传了简历;1: 开始面试;2: 面试完成;3. 面试分析完成;4. 异常中断
    status: Optional[int] = Field(
        None,
        description="0: 上传了简历;1: 开始面试;2: 面试完成;3. 面试分析完成;4. 异常中断"
    )
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
