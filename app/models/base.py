from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

# 创建 SQLAlchemy 基类
Base = declarative_base()


class BaseModel(Base):
    """
    所有模型的基类，提供通用字段和功能
    """

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    created_at = Column(
        DateTime, nullable=False, server_default=func.now(), comment="创建时间"
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )
