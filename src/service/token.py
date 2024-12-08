# self
from fastapi import HTTPException, Request
from do.user import User,UserCreate
from dao.user import UserDao
from config.fastapi_config import token_util
from service.user import UsersService,User
# lib
from passlib.context import CryptContext


import hashlib

# bcrypt加密  盐值加密,每一个盐值加密后的密码都不一样
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# pwd_context.hash(password)

class TokenService:
    """注册"""
    @staticmethod
    async def register(user: UserCreate)->str:
        """创建用户"""
        # Email重复
        if await UsersService.select_by_email(user.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        # 密码加密存入
        user_add = User()
        user_add.email = user.email
        # 默认 name
        # 使用SHA-256哈希算法，然后转换为十六进制格式
        hash_object = hashlib.sha256(user.email.encode())
        hex_dig = hash_object.hexdigest()
        user_add.name ='new user ' + hex_dig[:6]  # 返回前length个字符
        user_add.pwd = pwd_context.hash(user.pwd)
        return await UsersService.add(user_add)
    
    
    """token  用邮箱验证"""
    @staticmethod
    async def create_access_token(email:str,password:str):
        """生成token"""
        user =await TokenService.authenticate_user(email, password)
        if not user:
            raise HTTPException(
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        data={"sub": email}
        encoded_jwt = token_util.data2token(data)
        return encoded_jwt

    @staticmethod
    async def authenticate_user(email: str, password: str):
        """
        验证用户身份。

        :param fake_db: 模拟的用户数据库。
        :param username: 用户名。
        :param password: 明文密码。
        :return: 如果验证成功，返回用户对象；否则返回 False。
        """
        user =await UsersService.select_by_email(email)
        # 验证明文密码是否与已哈希的密码匹配
        if not user or not pwd_context.verify(password, user.password):
            return False
        return user


    # async def get_current_user(request: Request):
    #     """
    #     获取当前用户信息。

    #     :param token: Bearer 令牌。
    #     :return: 当前用户对象。
    #     :raises HTTPException: 如果无法验证凭据或用户不存在。
    #     """
    #     try:
    #         # decode 解码token内容
    #         payload = token_util.token_request2data(request)
    #         username: str = payload.get("sub")
    #         if username is None:
    #             raise credentials_exception
    #         token_data = TokenData(username=username)
    #     except InvalidTokenError:
    #         raise credentials_exception
    #     user = get_user(fake_users_db, username=token_data.username)
    #     if user is None:
    #         raise credentials_exception
    #     return user



    
# fake_users_db = {
#     "johndoe": {
#         "username": "johndoe",
#         "full_name": "John Doe",
#         "email": "johndoe@example.com",
#         # 明文 secret
#         "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
#         "disabled": False,
#     }
# }



# class TokenData(BaseModel):
#     username: str | None = None


# class User(BaseModel):
#     username: str
#     email: str | None = None
#     full_name: str | None = None
#     disabled: bool | None = None


# class UserInDB(User):
#     hashed_password: str

# def get_user(db, username: str):
#     if username in db:
#         user_dict = db[username]
#         return UserInDB(**user_dict)