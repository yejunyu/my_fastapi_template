# app/api/v1/endpoints/todos.py
import json
import os
import pathlib
import aiofiles
from fastapi import APIRouter, Depends
from app.core.response import UnifiedResponseRoute

from sqlalchemy.ext.asyncio import AsyncSession
from app import models, schemas
from app.api import deps
from app.schemas import chat
from app.services.zijie import sig
from app.services.zijie.genToken import AccessToken

router = APIRouter(prefix="/rtc", tags=["RTC"], route_class=UnifiedResponseRoute)


APPID = "686514454b4c3e017a63f89c"
KEY = "d6175d311284410f988c6b843e6dc4d5"
TTS_APPID = "4613407296"
TTS_KEY = "L1qb94kIq-LHwyrXL6QacuUf06lruODy"


@router.get("/getToken", response_model=schemas.Token)
async def get_token(
    *, current_user: models.User = Depends(deps.get_current_user)
) -> schemas.Token:
    """
    获取一个rtc的token
    该token用于rtc的房间创建和加入
    该token的uid为用户id
    """
    uid: str = str(current_user.id)
    token = AccessToken(uid, APPID, KEY)
    return schemas.Token(uid=uid, access_token=token.serialize())


@router.post("/getScenes", response_model=dict)
async def get_scene_config(
    *,
    request: chat.InterviewInfo,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> dict:
    """
    获取rtc配置
    """
    uid: str = str(current_user.id)
    # token = AccessToken(uid, APPID, KEY)
    # 面试配置
    PROJECT_ROOT = os.getenv("PROJECT_ROOT", str(pathlib.Path(__file__).parents[3]))
    prompt_path = pathlib.Path(PROJECT_ROOT) / "prompt" / "interview"
    async with aiofiles.open(prompt_path, "r", encoding="utf-8") as f:
        from jinja2 import Template

        prompt_template_str = await f.read()
        template = Template(prompt_template_str)
        prompt = template.render(
            job_intention=request.job_intention,
            resume_experience=request.resume_experience,
        )
    result = {
        "AppId": APPID,
        "RoomId": uid,
        "TaskId": request.task_id,
        "AgentConfig": {
            "TargetUserId": [uid],
            "WelcomeMessage": "你好，我是你今天的面试官刘聪, 要不你先做个简单的自我介绍吧？",
            "UserId": "ai" + uid,
            "EnableConversationStateCallback": True,
        },
        "Config": {
            "ASRConfig": {
                "Provider": "volcano",
                "ProviderParams": {
                    "Mode": "bigmodel",
                    "AppId": TTS_APPID,
                    "AccessToken": TTS_KEY,
                    "ApiResourceId": "volc.bigasr.sauc.duration",
                },
            },
            "TTSConfig": {
                "Provider": "volcano_bidirection",
                "ProviderParams": {
                    "app": {"appid": TTS_APPID, "token": TTS_KEY},
                    "audio": {
                        "voice_type": "zh_male_aojiaobazong_moon_bigtts",
                        "speech_rate": 0,
                        "pitch_rate": 0,
                    },
                    "ResourceId": "volc.service_type.10029",
                },
            },
            "SubtitleConfig": {"DisableRTSSubtitle": False, "SubtitleMode": 1},
            "LLMConfig": {
                "Mode": "ArkV3",
                "EndPointId": "ep-20250704135822-sbqhj",
                "SystemMessages": [prompt],
                "VisionConfig": {"Enable": False},
            },
            "InterruptMode": 1,
        },
    }
    return result


@router.post("/startVoiceChat", response_model=dict)
async def start_voice_chat(
    *,
    request: chat.VoiceChatIn,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> dict:
    """
    开始语音聊天
    """
    uid: str = str(current_user.id)
    config = json.loads(request.request)

    return sig.start_voice_chat(config)


@router.post("/stopVoiceChat", response_model=dict)
async def stop_voice_chat(
    *,
    request: chat.VoiceChatIn,
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> dict:
    """
    开始语音聊天
    """
    uid: str = str(current_user.id)
    task_id = request.request
    params = {
        "AppId": APPID,
        "RoomId": uid,
        "TaskId": task_id,
    }
    return sig.stop_voice_chat(params)