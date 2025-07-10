import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
from loguru import logger
from sqlalchemy import false, select
from app.core.config import settings
from app.db.session import AsyncSessionFactory  # 你的 async_session 工厂

from app.core.response import UnifiedResponseRoute
from app.core.exceptions import setup_exception_handlers
from app.core.middleware import setup_middlewares
from app.api.v1.api import api_router
from fastapi.middleware.cors import CORSMiddleware

# 配置 loguru 日志
import sys

from app.models.interview import Interview, InterviewStatus
from app.models.user import User
from app.crud import crud_user, crud_interview
from app.services.zijie import sig

logger.remove()  # 移除默认处理器
logger.add(
    sink=sys.stdout,  # 输出到控制台
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
)

HEARTBEAT_TIMEOUT = 60  # 心跳超时时间（秒）


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动定时任务
    asyncio.create_task(scan_interview_table())
    yield
    # 可选：在此处做清理工作


# --- FastAPI App 初始化 ---
app = FastAPI(title="My Interview AI Teacher", version="1.0.0", lifespan=lifespan)


async def scan_interview_table():
    """
    定时任务，每秒扫描一次interview表，处理正在进行的面试。
    1. 检查心跳是否超时。
    2. 对活跃的面试进行计费（扣除积分）。
    3. 积分不足或心跳超时则终止面试。
    """
    # 打印数据库连接信息
    logger.info(f"数据库连接信息: {settings.SQLALCHEMY_DATABASE_URI}")

    while True:
        try:
            async with AsyncSessionFactory() as session:
                # 1. 查询所有正在进行的面试
                result = await session.execute(
                    select(Interview).where(
                        Interview.status == InterviewStatus.START_INTERVIEW
                    )
                )
                interviews = result.scalars().all()

                if interviews:
                    logger.info(f"扫描到 {len(interviews)} 条正在进行的面试记录")

                for interview in interviews:
                    now = datetime.now(timezone.utc)
                    updated_at = getattr(interview, "updated_at", now)
                    # 2. 对活跃面试进行计费
                    user = await crud_user.get(session, int(interview.user_id))
                    if not user:
                        logger.error(
                            f"未找到面试 {interview.task_id} 对应的用户 {interview.user_id}"
                        )
                        continue

                    if getattr(user, "points", 0) > 0:
                        # 积分充足，扣除1点
                        await crud_user.update(
                            session, db_obj=user, obj_in={"points": user.points - 1}
                        )
                        logger.info(
                            f"用户 {user.id} 面试中，扣除1点积分，剩余 {user.points - 1} 点"
                        )
                    else:
                        # 积分不足，终止面试
                        logger.warning(
                            f"用户 {user.id} 积分不足，自动结束面试 {interview.task_id}"
                        )
                        sig.update_voice_chat_by_uid(
                            str(user.id),
                            str(interview.task_id),
                            "很抱歉的提示您,您的积分已经不足,请充值后继续面试",
                        )
                        sig.stop_voice_chat(
                            {
                                "RoomId": str(user.id),
                                "TaskId": interview.task_id,
                            }
                        )
                        await crud_interview.end_interview(
                            session,
                            interview,
                            InterviewStatus.EXCEPTION_INTERRUPTED,
                            "积分不足",
                        )

                    # 3. 检查心跳是否超时 (状态机逻辑)
                    time_delta = now - updated_at
                    notification_status = getattr(interview, "notification_status", 0)

                    # 状态0: 从未警告 -> 检查20秒超时
                    if notification_status == 0 and time_delta > timedelta(
                        seconds=HEARTBEAT_TIMEOUT / 2
                    ):
                        logger.warning(
                            f"面试 {interview.task_id} 20s未响应，发送警告。"
                        )
                        sig.update_voice_chat_by_uid(
                            str(user.id),
                            str(interview.task_id),
                            "请在20s内继续作答哦，否则系统将会自动终止本次面试！",
                        )
                        # 更新状态到1
                        await crud_interview.update(
                            session, db_obj=interview, obj_in={"notification_status": 1}
                        )

                    # 状态1: 已发送20秒警告 -> 检查40秒超时
                    elif notification_status == 1 and time_delta > timedelta(
                        seconds=HEARTBEAT_TIMEOUT
                    ):
                        logger.warning(
                            f"面试 {interview.task_id} 心跳超时40s，发送最终警告。"
                        )
                        sig.update_voice_chat_by_uid(
                            str(user.id),
                            str(interview.task_id),
                            "未在规定时间内作答，本次面试到此结束，请在本页面耐心等待查收面试分析结果！",
                        )
                        # 更新状态到2
                        await crud_interview.update(
                            session, db_obj=interview, obj_in={"notification_status": 2}
                        )

                    # 状态2: 已发送最终警告 -> 检查45秒超时并终止
                    elif notification_status == 2 and time_delta > timedelta(
                        seconds=HEARTBEAT_TIMEOUT + 5
                    ):
                        logger.warning(f"面试 {interview.task_id} 超时，自动结束。")
                        sig.stop_voice_chat(
                            {
                                "RoomId": str(user.id),
                                "TaskId": interview.task_id,
                            }
                        )
                        await crud_interview.end_interview(
                            session,
                            interview,
                            InterviewStatus.EXCEPTION_INTERRUPTED,
                            f"心跳超时（超过{HEARTBEAT_TIMEOUT + 5}秒未活动）",
                        )
                        continue  # 处理下一个
        except Exception as e:
            logger.error(f"定时扫描任务发生异常: {e}")

        await asyncio.sleep(1)  # 每秒执行一次


# 应用统一响应封装
app.router.route_class = UnifiedResponseRoute

# 注册异常处理器
setup_exception_handlers(app)

# 注册中间件
setup_middlewares(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
