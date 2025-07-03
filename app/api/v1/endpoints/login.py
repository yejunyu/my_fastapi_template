# app/api/v1/endpoints/login.py
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app import crud, schemas
from app.api import deps
from app.core.security import create_access_token
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/users", tags=["用户相关"])


@router.post("/register", response_model=schemas.UserPublic)
async def register_new_user(
    *,
    db_session: AsyncSession = Depends(deps.get_db),
    user_in: schemas.UserCreate,
) -> Any:
    """
    创建新用户。
    """
    user = await crud.user.get_by_phone(db_session, phone=user_in.phone)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this phone already exists in the system.",
        )

    user = await crud.user.create(db_session, obj_in=user_in)
    return user


@router.post("/login/access-token", response_model=schemas.Token)
async def login_access_token(
    db_session: AsyncSession = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 兼容的 token 登录，获取 access token.
    """
    # form_data.username 将会是我们的手机号
    user = await crud.user.authenticate(
        db_session, phone=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.phone)
    return {"access_token": access_token, "token_type": "bearer"}
