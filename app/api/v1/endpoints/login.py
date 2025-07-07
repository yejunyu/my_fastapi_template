# app/api/v1/endpoints/login.py
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from app import crud, schemas, models
from app.api import deps
from app.core.security import create_access_token, get_password_hash
from app.core.password_validator import validate_password_strength
from app.services.email import email_service
from app.services.auth import auth_service
from app.core.response import UnifiedResponseRoute

router = APIRouter(prefix="/users", tags=["用户认证"], route_class=UnifiedResponseRoute)
# router = APIRouter(prefix="/users", tags=["用户认证"])

# 简单的内存缓存用于频率限制（生产环境应使用Redis）
_rate_limit_cache: dict[str, datetime] = {}


def check_rate_limit(key: str, seconds: int = 60) -> bool:
    """检查频率限制"""
    now = datetime.now(timezone.utc)
    if key in _rate_limit_cache:
        if now - _rate_limit_cache[key] < timedelta(seconds=seconds):
            return False
    _rate_limit_cache[key] = now
    return True


@router.post("/send-verification-code")
async def send_verification_code(
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    email_data: schemas.SendVerificationCode,
) -> schemas.Msg:
    """
    发送邮箱验证码
    """
    # 频率限制检查
    if not check_rate_limit(f"email:{email_data.email}", 60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="请求过于频繁，请60秒后再试",
        )

    # 检查邮箱是否已注册
    existing_user = await crud.user.get_by_email(db_session, email=email_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册，请直接登录或找回密码",
        )

    # 生成验证码
    code = email_service.generate_verification_code()

    # 保存验证码到数据库
    await crud.email_verification.create_code(
        db_session, email=email_data.email, code=code
    )

    # 发送邮件
    success = await email_service.send_verification_code(email_data.email, code)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="发送验证码失败，请稍后重试",
        )

    return schemas.Msg(msg="验证码已发送至您的邮箱，请注意查收")


@router.post("/register", response_model=schemas.UserPublic)
async def register_new_user(
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    user_in: schemas.UserCreate,
) -> models.User:
    """
    用户注册（需要验证码）
    """
    # 检查邮箱是否已注册
    existing_user = await crud.user.get_by_email(db_session, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册，请直接登录或找回密码",
        )

    # 校验密码强度
    is_valid, password_errors = validate_password_strength(user_in.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"密码强度不足: {'; '.join(password_errors)}",
        )

    # 验证验证码
    code_obj = await crud.email_verification.get_valid_code(
        db_session, email=user_in.email, code=user_in.verification_code
    )
    if not code_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期，请重新获取",
        )

    # 标记验证码为已使用
    await crud.email_verification.mark_as_used(db_session, code_obj=code_obj)

    # 创建用户
    user = await crud.user.create(db_session, obj_in=user_in)
    return user


@router.post("/login", response_model=schemas.Token)
async def login(
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
    login_type: str = Form(default="password"),
) -> schemas.Token:
    """
    用户登录（表单提交）
    """
    # 使用认证策略进行身份验证
    user = await auth_service.authenticate(
        db_session,
        strategy=login_type,
        email=form_data.username,
        password=form_data.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 检查用户状态
    if str(user.status) != models.UserStatus.ACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="账户未激活，请联系管理员"
        )

    # 生成访问令牌
    access_token = create_access_token(subject=user.id)
    return schemas.Token(uid=str(user.id), access_token=access_token)


@router.post("/forgot-password")
async def forgot_password(
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    email_data: schemas.ForgotPassword,
) -> schemas.Msg:
    """
    忘记密码，发送重置链接
    """
    # 频率限制检查
    if not check_rate_limit(f"reset:{email_data.email}", 300):  # 5分钟限制
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="请求过于频繁，请5分钟后再试",
        )

    # 检查用户是否存在
    user = await crud.user.get_by_email(db_session, email=email_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="该邮箱未注册"
        )

    # 生成重置token
    reset_token_obj = await crud.password_reset.create_token(
        db_session, user_id=int(user.id)  # type: ignore
    )

    # 发送重置邮件
    success = await email_service.send_password_reset_link(
        email_data.email, str(reset_token_obj.token)
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="发送重置邮件失败，请稍后重试",
        )

    return schemas.Msg(msg="密码重置邮件已发送至您的邮箱，请注意查收")


@router.post("/reset-password")
async def reset_password(
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    reset_data: schemas.ResetPassword,
) -> schemas.Msg:
    """
    重置密码
    """
    # 验证重置token
    token_obj = await crud.password_reset.get_valid_token(
        db_session, token=reset_data.token
    )
    if not token_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="重置链接无效或已过期，请重新申请",
        )

    # 校验新密码强度
    is_valid, password_errors = validate_password_strength(reset_data.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"密码强度不足: {'; '.join(password_errors)}",
        )

    # 获取用户
    user = await crud.user.get(db_session, id=token_obj.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    # 更新用户密码
    hashed_password = get_password_hash(reset_data.new_password)
    await crud.user.update(
        db_session, db_obj=user, obj_in={"hashed_password": hashed_password}
    )

    # 标记token为已使用
    await crud.password_reset.mark_as_used(db_session, token_obj=token_obj)

    return schemas.Msg(msg="密码修改成功，请使用新密码登录")


@router.get("/me", response_model=schemas.UserPublic)
async def get_current_user_info(
    current_user: models.User = Depends(deps.get_current_user),
) -> models.User:
    """
    获取当前用户信息
    """
    print(f"当前用户: {current_user.status}, ID: {current_user.id}")
    return current_user


@router.put("/me", response_model=schemas.UserPublic)
async def update_current_user(
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_user),
) -> models.User:
    """
    更新当前用户信息
    """
    # 如果要更新密码，验证密码强度
    if user_update.password:
        is_valid, password_errors = validate_password_strength(user_update.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"密码强度不足: {'; '.join(password_errors)}",
            )

    # 如果要更新邮箱，检查邮箱是否已被占用
    if user_update.email and user_update.email != current_user.email:
        existing_user = await crud.user.get_by_email(
            db_session, email=user_update.email
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="该邮箱已被其他用户使用"
            )

    # 更新用户信息
    user = await crud.user.update(db_session, db_obj=current_user, obj_in=user_update)
    return user
