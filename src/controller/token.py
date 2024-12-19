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
from do.token import Token
from do.user import UserCreate
from service.token import TokenService

# to get a string like this run:
# openssl rand -hex 32


router = APIRouter()

# # 验证邮箱
# @router.post("/verify_email", summary="post 验证邮箱")
# async def verify_email(token: str):
#     """验证邮箱   todo网易"""
#     return await TokenService.verify_email(token)

# 注册
@router.post("/register", summary="post 注册")
async def register(user: UserCreate)->str:
    """注册"""
    # 邮箱
    return await TokenService.register(user)



@router.post("/email", summary="post 获取访问令牌")
async def login_for_access_token_by_email(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    """
    首次登陆，账户密码获取访问令牌。
    :param form_data: 包含用户名和密码的表单数据。
    :return: 包含访问令牌和令牌类型的响应。
    """
    # username可以是email 或者username或tel
    encoded_jwt =await TokenService.create_access_token(
        form_data.username, form_data.password
    )
    token = Token(access_token=encoded_jwt, token_type="Bearer")
    return token
@router.post("/tel", summary="post 获取访问令牌")
async def login_for_access_token_by_tel(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    """
    首次登陆，账户密码获取访问令牌。
    :param form_data: 包含用户名和密码的表单数据。
    :return: 包含访问令牌和令牌类型的响应。
    """
    # username可以是email 或者username或tel
    encoded_jwt =await TokenService.create_access_token(
        form_data.username, form_data.password
    )
    token = Token(access_token=encoded_jwt, token_type="Bearer")
    return token


# @router.get("/users/me/", response_model=User)
# async def read_users_me(
#     current_user: Annotated[User, Depends(get_current_active_user)],
# ):
#     return current_user




app.include_router(router, prefix="/token", tags=["验证"])
