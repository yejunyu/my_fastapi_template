# app/api/v1/endpoints/login.py
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm

from app import crud, schemas
from app.api import deps
from app.core.security import create_access_token
from app.core.config import settings
from app.services.email_service import email_service
from app.models.email_verification import VerificationType
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/register", response_model=schemas.UserResponse)
async def register_new_user(
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    background_tasks: BackgroundTasks,
) -> Any:
    """
    创建新用户并发送激活邮件。
    """
    # 检查邮箱是否已存在
    user = await crud.user.get_by_email(db_session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    # 如果提供了手机号，检查是否已存在
    if user_in.phone:
        existing_phone_user = await crud.user.get_by_phone(
            db_session, phone=user_in.phone
        )
        if existing_phone_user:
            raise HTTPException(
                status_code=400,
                detail="The user with this phone already exists in the system.",
            )

    # 创建新用户
    user = await crud.user.create(db_session, obj_in=user_in)

    # 创建激活token
    verification = await crud.email_verification.create_verification_token(
        db_session,
        user_id=user.id,
        email=user.email,
        verification_type=VerificationType.ACTIVATION,
        expire_hours=settings.EMAIL_VERIFICATION_EXPIRE_HOURS,
    )

    # 构建激活链接
    activation_link = f"{settings.FRONTEND_URL}/activate?token={verification.token}"

    # 后台发送激活邮件
    background_tasks.add_task(
        email_service.send_activation_email,
        to_email=user.email,
        username=user.email.split("@")[0],  # 使用邮箱用户名部分
        activation_link=activation_link,
    )

    return schemas.UserResponse(
        message="用户注册成功，请检查您的邮箱并点击激活链接来激活账户", email=user.email
    )


@router.post("/login/access-token", response_model=schemas.Token)
async def login_access_token(
    db_session: AsyncSession = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 兼容的 token 登录，获取 access token.
    支持邮箱登录。
    """
    # form_data.username 现在是邮箱地址
    user = await crud.user.authenticate_by_email(
        db_session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password, or account not activated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.email)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/activate/{token}", response_model=schemas.UserResponse)
async def activate_account(
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    token: str,
) -> Any:
    """
    激活用户账户
    """
    # 验证并使用激活token
    verification = await crud.email_verification.verify_and_use_token(
        db_session, token=token, verification_type=VerificationType.ACTIVATION
    )

    if not verification:
        raise HTTPException(
            status_code=400, detail="Invalid or expired activation token"
        )

    # 获取用户并激活
    user = await crud.user.get(db_session, id=verification.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 激活用户
    user = await crud.user.activate_user(db_session, user=user)

    return schemas.UserResponse(
        message="账户激活成功，您现在可以登录了", email=user.email
    )


@router.post("/password-reset/request", response_model=schemas.UserResponse)
async def request_password_reset(
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    password_reset_request: schemas.PasswordResetRequest,
    background_tasks: BackgroundTasks,
) -> Any:
    """
    请求密码重置，发送重置邮件
    """
    # 查找用户
    user = await crud.user.get_by_email(db_session, email=password_reset_request.email)
    if not user:
        # 为了安全，不暴露用户是否存在
        return schemas.UserResponse(
            message="如果该邮箱存在，我们已发送密码重置链接",
            email=password_reset_request.email,
        )

    # 检查用户是否已激活
    if not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Account not activated. Please activate your account first.",
        )

    # 创建密码重置token
    verification = await crud.email_verification.create_verification_token(
        db_session,
        user_id=user.id,
        email=user.email,
        verification_type=VerificationType.PASSWORD_RESET,
        expire_hours=settings.EMAIL_VERIFICATION_EXPIRE_HOURS,
    )

    # 构建重置链接
    reset_link = f"{settings.FRONTEND_URL}/password-reset?token={verification.token}"

    # 后台发送重置邮件
    background_tasks.add_task(
        email_service.send_password_reset_email,
        to_email=user.email,
        username=user.email.split("@")[0],
        reset_link=reset_link,
    )

    return schemas.UserResponse(
        message="如果该邮箱存在，我们已发送密码重置链接",
        email=password_reset_request.email,
    )


@router.post("/password-reset/confirm", response_model=schemas.UserResponse)
async def confirm_password_reset(
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    password_reset_confirm: schemas.PasswordResetConfirm,
) -> Any:
    """
    确认密码重置
    """
    # 验证并使用重置token
    verification = await crud.email_verification.verify_and_use_token(
        db_session,
        token=password_reset_confirm.token,
        verification_type=VerificationType.PASSWORD_RESET,
    )

    if not verification:
        raise HTTPException(
            status_code=400, detail="Invalid or expired password reset token"
        )

    # 获取用户
    user = await crud.user.get(db_session, id=verification.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 更新密码
    user = await crud.user.update_password(
        db_session, user=user, new_password=password_reset_confirm.new_password
    )

    return schemas.UserResponse(
        message="密码重置成功，请使用新密码登录", email=user.email
    )
