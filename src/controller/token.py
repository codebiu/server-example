""" token controller"""

# self
from config.fastapi_config import app, token_util

# lib
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel
from do.token import Token

# to get a string like this run:
# openssl rand -hex 32


router = APIRouter()


@app.post("/", summary="post 获取访问令牌")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm,
) -> Token:
    """
    首次登陆，账户密码获取访问令牌。

    :param form_data: 包含用户名和密码的表单数据。
    :return: 包含访问令牌和令牌类型的响应。
    """
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = token_util.data2token(data={"sub": user.username})
    return token


@router.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user

app.include_router(router, prefix="/token", tags=["验证"])
