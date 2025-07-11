from enum import IntEnum
from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String, Text

from .base import BaseModel


class InterviewStatus(IntEnum):
    UPLOAD_RESUME = 0
    START_INTERVIEW = 1
    INTERVIEW_COMPLETED = 2
    INTERVIEW_ANALYSIS_COMPLETED = 3
    EXCEPTION_INTERRUPTED = 4


class OrderStatus(IntEnum):
    UNPAID = 0
    PAID = 1
    COMPLETED = 2


class Interview(BaseModel):
    __tablename__ = "interview"
    user_id = Column(Integer, nullable=False)
    task_id = Column(String(255), nullable=False)
    status = Column(
        Integer,
        default=InterviewStatus.UPLOAD_RESUME,
        nullable=False,
        comment="0: 上传了简历;1: 开始面试;2: 面试完成;3. 面试分析完成;4. 异常中断",
    )
    notification_status = Column(
        Integer,
        default=0,
        nullable=False,
        comment="通知状态: 0-未通知, 1-20s警告, 2-40s警告",
    )
    interview_result = Column(JSON, default={}, comment="面试结果")
    end_time = Column(DateTime(timezone=True), nullable=True, comment="面试结束时间")
    extra = Column(Text, default="", comment="额外信息")
    duration = Column(Integer, default=0, comment="面试时长，单位秒")
    delete_flag = Column(Boolean, default=False)


class Order(BaseModel):
    __tablename__ = "order"
    user_id = Column(Integer, nullable=False)
    order_no = Column(String(255), nullable=False)
    product_id = Column(String(255), nullable=False, comment="商品ID")
    status = Column(
        Integer,
        default=OrderStatus.UNPAID,
        nullable=False,
        comment="0: 未支付; 1: 支付完成; 2: 交易完成",
    )
    amount = Column(Integer, nullable=False, comment="订单金额，单位分")
