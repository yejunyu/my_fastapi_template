import json
import re
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
import os
import pdfplumber
import docx
import aiofiles
import pathlib

from sqlalchemy.ext.asyncio import AsyncSession
from app import models
from app.api import deps
from app.crud import user_file
from app.schemas.user_file import UserFileCreate, UserFilePublic
from loguru import logger

from openai import AsyncOpenAI
from app.core.response import UnifiedResponseRoute

router = APIRouter(prefix="/chat", tags=["ai相关"], route_class=UnifiedResponseRoute)


client = AsyncOpenAI(
    api_key="736cdaef-3e01-4197-83cd-373644c3ac6c",
    base_url="https://ark.cn-beijing.volces.com/api/v3",
)


@router.post("/upload-file", response_model=UserFilePublic)
async def upload_file(
    file: UploadFile = File(...),
    db_session: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    上传pdf/doc/docx文件，抽取文本并保存到数据库
    """
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
    logger.info(f"file_in: {text}")
    db_obj = await user_file.create(db_session, obj_in=file_in)

    # 删除临时文件
    try:
        os.remove(save_path)
    except Exception:
        logger.error(f"删除临时文件失败: {save_path}")

    # 抽取简历信息
    PROJECT_ROOT = os.getenv("PROJECT_ROOT", str(pathlib.Path(__file__).parents[3]))
    prompt_path = pathlib.Path(PROJECT_ROOT) / "prompt" / "resume_extract"
    async with aiofiles.open(prompt_path, "r", encoding="utf-8") as f:
        from jinja2 import Template

        prompt_template_str = await f.read()
        template = Template(prompt_template_str)
        prompt = template.render(resume_text=text)
    job_intention = None
    resume_experience = None
    try:
        completion = await client.chat.completions.create(
            model="ep-20250704152034-hcjqt",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )

        resp = completion.choices[0].message.content
        data = get_json(resp)
        job_intention = data.get("job_intention")
        resume_experience = data.get("resume_experience")
    except Exception as e:
        logger.error(f"简历信息抽取失败: {e}")

    # 更新数据库，写入抽取字段
    if job_intention or resume_experience:
        await user_file.update(
            db_session,
            db_obj=db_obj,
            obj_in={
                "job_intention": job_intention,
                "resume_experience": resume_experience,
            },
        )

    return db_obj


def get_json(md_text):
    pattern = r"```json\s*(.*?)\s*```"
    match = re.search(pattern, md_text, re.DOTALL)

    if match:
        json_str = match.group(1)
        data = json.loads(json_str)
        return data
    else:
        return {}
