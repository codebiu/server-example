# self
from fastapi import HTTPException, Request
from do.token import TokenType
from do.user import User, UserCreate
from dao.user import UserDao
from config.fastapi_config import token_util
from service.user import UserService, User

# lib
from passlib.context import CryptContext


import hashlib

# bcrypt加密  盐值加密,每一个盐值加密后的密码都不一样
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenService:
    """注册"""

    @staticmethod
    async def register(user: UserCreate) -> str:
        """
        使用email创建用户
        取hash内容前6个字符作为name标识：new user 123456
        """
        # Email重复
        if await UserService.select_by_email(user.email):
            raise HTTPException(status_code=400, detail="email registered")
        # 密码加密存入
        user_add = User()
        user_add.email = user.email
        # 默认 name
        # 使用SHA-256哈希算法，然后转换为十六进制格式
        hash_object = hashlib.sha256(user.email.encode())
        hex_dig = hash_object.hexdigest()
        user_add.name = "new user " + hex_dig[:6]  # 返回前length个字符
        # 加密密码
        user_add.pwd = pwd_context.hash(user.pwd)
        return await UserService.add(user_add)

    @staticmethod
    async def create_token(tokenType: TokenType, value: str, password: str):
        """生成token 用邮箱验证"""
        user: User = await TokenService.get_user(tokenType, value, password)
        # 验证明文密码是否与已哈希的密码匹配
        if not user or not pwd_context.verify(password, user.pwd):
            return False
        if not user:
            raise HTTPException(
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        data: dict[TokenType, str] = {"sub": user.id}
        encoded_jwt = token_util.data2token(data)
        return encoded_jwt

    @staticmethod
    async def get_user(type: TokenType, value: str) -> User:
        """
        验证用户身份。
        :param fake_db: 模拟的用户数据库。
        :param username: 用户名。
        :param password: 明文密码。
        :return: 如果验证成功，返回用户对象；否则返回 False。
        """
        if type == TokenType.email:
            user = await UserService.select_by_email(value)
        elif type == TokenType.tel:
            user = await UserService.select_by_tel(value)
        elif type == TokenType.out_token:
            # user = await UserService.select_by_tel(value)
            # TODO 外部token验证  邮箱  谷歌账号  微信扫码  手机号
            pass
        else:
            raise HTTPException(status_code=400, detail="type error")
        return user

    async def get_current_user(request: Request):
        """
        获取当前用户信息。
        :param token: Bearer 令牌。
        :return: 当前用户对象。
        :raises HTTPException: 如果无法验证凭据或用户不存在。
        """
        # decode 解码token内容
        try:
            payload: dict[TokenType, str] = token_util.token_request2data(request)
            id: str = payload.get("sub")
            user = await UserService.select(id)
        except Exception as e:
            info = str(e)
            raise HTTPException(status_code=400, detail="token error{info}")     
        if not user:
            raise HTTPException(status_code=400, detail="token not find")
        # 激活 封禁
        if user.disabled:
            raise HTTPException(status_code=400, detail="Inactive user")
        return user

