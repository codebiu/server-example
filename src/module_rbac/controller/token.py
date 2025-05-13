""" token controller"""

# self
from config.server import app

# lib

from fastapi import APIRouter, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm

from module_main.do.token import Token, TokenType
from module_main.do.user import UserCreate
from module_main.service.token import TokenService

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
async def register(user: UserCreate) -> str:
    """注册"""
    # 邮箱
    return await TokenService.register(user)


@router.post("/login", summary="email和password获取访问令牌")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    type: TokenType = Form(...),# ...必填
) -> Token:
    encoded_jwt = await TokenService.create_token(
        type, form_data.username, form_data.password
    )
    token = Token(access_token=encoded_jwt, token_type="Bearer")
    return token


# login_by_out_token


# @router.get("/users/me/", response_model=User)
# async def read_users_me(
#     current_user: Annotated[User, Depends(get_current_active_user)],
# ):
#     return current_user
# captcha

app.include_router(router, prefix="/token", tags=["验证"])
