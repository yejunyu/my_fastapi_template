from datetime import datetime, timedelta, timezone
import json
import re
import uuid
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Request,
    Form,
)
import os
import pdfplumber
import docx
import aiofiles
import pathlib

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from app import models
from app.api import deps
from app.crud import crud_interview, crud_user, user_file, crud_chat_log
from app.models.interview import Interview, InterviewStatus
from app.schemas.user_file import UserFileCreate, UserFilePublic
from loguru import logger

from openai import AsyncOpenAI
from app.core.response import UnifiedResponseRoute
from app.services.zijie import rtc_callback, sig
from app.utils.prompt_loader import prompt_loader
from app.schemas.chat import ChatLogCreate, ChatLogUpdate
from app.schemas.interview import InterviewOut
from app.core.exceptions import BusinessException, BusinessErrorCode

router = APIRouter(prefix="/chat", tags=["ai相关"], route_class=UnifiedResponseRoute)


client = AsyncOpenAI(
    api_key="736cdaef-3e01-4197-83cd-373644c3ac6c",
    base_url="https://ark.cn-beijing.volces.com/api/v3",
)


@router.post("/upload-file", response_model=dict)
async def upload_file(
    file: UploadFile = File(...),
    task_id: str = Form(...),
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.require_points(60 * 45)),
):
    """
    上传pdf/doc/docx文件，抽取文本并保存到数据库
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")
    filename = file.filename
    ext = filename.split(".")[-1].lower()
    if ext not in {"pdf", "doc", "docx"}:
        raise HTTPException(status_code=400, detail="仅支持pdf, doc, docx文件")

    # 保存文件到 /tmp 目录
    file_id = str(uuid.uuid4())
    save_name = f"{file_id}.{ext}"
    save_path = os.path.join("/tmp", save_name)
    file.file.seek(0)
    async with aiofiles.open(save_path, "wb") as out_file:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            await out_file.write(chunk)

    # 文本抽取
    text = ""
    if ext == "pdf":
        with pdfplumber.open(save_path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    elif ext == "docx":
        doc = docx.Document(save_path)
        text = "\n".join([p.text for p in doc.paragraphs])

    # 入库（先插入基本信息）
    file_in = UserFileCreate(
        filename=filename,
        file_path=save_path,
        file_type=ext,
        text_content=text,
        user_id=getattr(current_user, "id", None),
    )
    await user_file.create(db_session, obj_in=file_in)

    # 删除临时文件
    try:
        os.remove(save_path)
    except Exception:
        logger.error(f"删除临时文件失败: {save_path}")

    # 抽取简历信息
    PROJECT_ROOT = os.getenv("PROJECT_ROOT", str(pathlib.Path(__file__).parents[3]))
    prompt_path = pathlib.Path(PROJECT_ROOT) / "prompt" / "resume_prompt"
    async with aiofiles.open(prompt_path, "r", encoding="utf-8") as f:

        prompt_template_str = await f.read()
    job_intention = None
    resume_experience = None
    try:
        completion = await client.chat.completions.create(
            # model="ep-20250704152034-hcjqt",
            model="ep-20250707161556-qfjs8",
            messages=[
                {"role": "system", "content": prompt_template_str},
                {"role": "user", "content": text},
            ],
            temperature=0.2,
        )

        resp = completion.choices[0].message.content
        if not resp:
            raise HTTPException(status_code=500, detail="AI响应为空")
        data = get_json(resp)
        print(data)
        job_intention = data.get("job_intention", "")
        resume_experience = data.get("resume_experience")
    except Exception as e:
        logger.error(f"简历信息抽取失败: {e}")
        raise BusinessException(
            error_enum=BusinessErrorCode.SYSTEM_ERROR,
            msg="简历信息抽取失败",
        )

    # 更新数据库，写入抽取字段

    if job_intention or resume_experience:
        new_interview = Interview(
            user_id=current_user.id,
            task_id=task_id,
            interview_result={
                "score_weight": data.get("score_weight"),
                "resume_analysis": data.get("resume_analysis"),
            },
        )
        db_session.add(new_interview)
        await db_session.commit()
        await db_session.refresh(new_interview)

    return data


def get_json(md_text: str) -> dict:
    pattern = r"```json\s*(.*?)\s*```"
    match = re.search(pattern, md_text, re.DOTALL)

    if match:
        json_str = match.group(1)
        data = json.loads(json_str)
        return data
    else:
        return json.loads(md_text)


@router.get("/list/interview_result", response_model=list[InterviewOut])
async def list_interview_result(
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    获得面试结果
    """
    user_id = getattr(current_user, "id", None)
    if user_id is None:
        raise HTTPException(status_code=400, detail="用户ID无效")
    interviews = await crud_interview.get_interview_result_by_uid(
        db_session, int(user_id)
    )
    return [
        InterviewOut.model_validate(interview, from_attributes=True)
        for interview in interviews
    ]


async def assemble_chat_logs(db: AsyncSession, task_id: str) -> list:
    chat_logs = await crud_chat_log.get_chat_logs_by_taskid(db, task_id)
    result = []
    for log in chat_logs:
        role = "interviewer" if getattr(log, "is_ai", False) else "candidate"
        result.append(
            {
                "role": role,
                "message": getattr(log, "message", ""),
            }
        )
    return result


@router.get("/detail/interview_result/{task_id}", response_model=InterviewOut)
async def detail_interview_result(
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    task_id: str,
):
    """
    获得面试结果详情
    """
    uid = getattr(current_user, "id", 0)
    interview = await crud_interview.get_by_task_id(db_session, task_id, uid)
    if not interview:
        raise BusinessException(
            error_enum=BusinessErrorCode.INTERVIEW_NOT_FOUND, msg="面试结果不存在"
        )
    if getattr(interview, "status", None) != InterviewStatus.INTERVIEW_COMPLETED.value:
        raise BusinessException(
            error_enum=BusinessErrorCode.INTERVIEW_NOT_COMPLETED, msg="面试结果未完成"
        )
    # 面试时间不足20分钟
    if getattr(interview, "duration", 0) < 20 * 60:
        raise BusinessException(
            error_enum=BusinessErrorCode.INTERVIEW_DURATION_TOO_SHORT,
            msg="面试时间不足20分钟,无法生成面试报告,请重新面试",
        )
    chat_logs = await assemble_chat_logs(db_session, task_id)
    logs = json.dumps(chat_logs, ensure_ascii=False)
    prompt_template_str = prompt_loader.format_prompt(
        "ranking", interview_dialogue=logs
    )
    completion = await client.chat.completions.create(
        # model="ep-20250704152034-hcjqt",
        model="ep-20250707161556-qfjs8",
        messages=[
            {"role": "user", "content": prompt_template_str},
        ],
        temperature=0.2,
    )
    resp = completion.choices[0].message.content
    if not resp:
        raise HTTPException(status_code=500, detail="AI响应为空")
    data = get_json(resp)

    # 使用 crud.update 更新
    update_data = {
        "interview_result": {
            **(interview.interview_result or {}),
            "interview_result": data,
        },
        "status": InterviewStatus.INTERVIEW_ANALYSIS_COMPLETED.value,
    }

    updated_interview = await crud_interview.update(
        db=db_session, db_obj=interview, obj_in=update_data
    )

    return InterviewOut.model_validate(updated_interview, from_attributes=True)


@router.post("/chat_callback")
async def chat_callback(
    *, request: Request, db_session: AsyncSession = Depends(deps.get_db)
):
    """
    语音面试回调
    """
    body = await request.body()
    data = json.loads(body)
    message = data.get("message")
    resp = rtc_callback.unpack_subtitle_message(message)
    if resp:
        logger.info(f"chat_callback: {resp}")
        data = resp.get("data", [])[0]
        chat_log = data.get("text")
        if chat_log:
            uid: str = data.get("userId")
            is_ai: bool = uid.startswith("ai")
            # 扣减积分
            if is_ai:
                uid = uid[2:]
            interview = await crud_interview.get_interviewing_by_uid(
                db_session, int(uid)
            )
            if interview:
                if not is_ai:
                    user = await crud_user.get(db_session, int(uid))
                    if user:
                        if getattr(user, "points", 0) <= 0:
                            logger.error(f"用户 {uid} 积分不足，停止面试")
                            sig.update_voice_chat_by_uid(
                                uid,
                                str(interview.task_id),
                                "很抱歉的提示您,您的积分已经不足,请充值后继续面试",
                            )
                            sig.stop_voice_chat(
                                {
                                    "RoomId": uid,
                                    "TaskId": interview.task_id,
                                }
                            )
                            await crud_interview.end_interview(
                                db_session,
                                interview,
                                InterviewStatus.EXCEPTION_INTERRUPTED,
                                "积分不足",
                            )
                            return {"error": "积分不足"}
                    # 更新面试时间
                    await crud_interview.update_updated_at_by_uid_taskid(
                        db_session, int(uid), str(interview.task_id)
                    )
                # 记录聊天记录
                chat_log_in = ChatLogCreate(
                    user_id=uid,
                    task_id=str(interview.task_id),
                    message=chat_log,
                    is_ai=is_ai,
                )
                await crud_chat_log.create(db_session, obj_in=chat_log_in)
                # 查看面试时间是否超过20分钟
                now = datetime.now(timezone.utc)
                if (created_at := getattr(interview, "created_at", None)) and (
                    now - created_at > timedelta(minutes=45)
                ):
                    sig.update_voice_chat_by_uid(
                        uid,
                        str(interview.task_id),
                        "感谢您的面试，本次面试到此结束，请在本页面耐心等待查收面试分析结果！",
                    )
                    sig.stop_voice_chat(
                        {
                            "RoomId": uid,
                            "TaskId": interview.task_id,
                        }
                    )
                    await crud_interview.end_interview(
                        db_session, interview, InterviewStatus.INTERVIEW_COMPLETED
                    )
    return {}
