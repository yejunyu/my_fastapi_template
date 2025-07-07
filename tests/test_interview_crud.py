from unittest import result
import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from app.models.interview import Interview, InterviewStatus
from app.models.base import BaseModel, Base
from sqlalchemy import select
import os

DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", "postgresql+asyncpg://root:123456@localhost:5432/interview"
)

# 创建异步引擎和会话
engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


@pytest.fixture(scope="module", autouse=True)
async def setup_database():
    # 创建表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # 删除表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture()
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.mark.asyncio
async def test_create_interview(db_session):
    interview = Interview(
        user_id=1, task_id="task1", status=InterviewStatus.START_INTERVIEW.value
    )
    db_session.add(interview)
    await db_session.commit()
    await db_session.refresh(interview)
    assert interview.id is not None
    assert interview.user_id == 1
    assert interview.task_id == "task1"


@pytest.mark.asyncio
async def test_read_interview(db_session):
    # 先插入
    interview = Interview(
        user_id=2, task_id="task2", status=InterviewStatus.START_INTERVIEW.value
    )
    db_session.add(interview)
    await db_session.commit()
    await db_session.refresh(interview)
    # 查询
    stmt = select(Interview).where(Interview.user_id == 2, Interview.task_id == "task2")
    result = await db_session.execute(stmt)
    found = result.scalar_one_or_none()
    assert found is not None
    assert found.user_id == 2
    assert found.task_id == "task2"


@pytest.mark.asyncio
async def test_update_interview(db_session):
    # 先插入
    interview = Interview(
        user_id=3, task_id="task3", status=InterviewStatus.START_INTERVIEW.value
    )
    db_session.add(interview)
    await db_session.commit()
    await db_session.refresh(interview)
    # 更新
    interview.status = InterviewStatus.INTERVIEW_COMPLETED.value
    await db_session.commit()
    await db_session.refresh(interview)
    assert interview.status == InterviewStatus.INTERVIEW_COMPLETED.value


@pytest.mark.asyncio
async def test_delete_interview(db_session):
    # 先插入
    interview = Interview(
        user_id=4, task_id="task4", status=InterviewStatus.START_INTERVIEW.value
    )
    db_session.add(interview)
    await db_session.commit()
    await db_session.refresh(interview)
    # 删除
    await db_session.delete(interview)
    await db_session.commit()
    # 查询确认删除
    stmt = select(Interview).where(Interview.user_id == 4, Interview.task_id == "task4")
    result = await db_session.execute(stmt)
    found = result.scalar_one_or_none()
    assert found is None


@pytest.mark.asyncio
async def test_interview_json(db_session):
    stmt = select(Interview).where(Interview.task_id == "123")
    result = await db_session.execute(stmt)
    interview = result.scalar_one_or_none()
    assert interview is not None
    assert interview.interview_result == {}
