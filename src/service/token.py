# self
from do.user import User,UserCreate
from dao.user import UserDao

# lib
from passlib.context import CryptContext

# bcrypt加密  盐值加密,每一个盐值加密后的密码都不一样
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# pwd_context.hash(password)

class TokenService:
    """token"""

    @staticmethod
    def authenticate_user(username: str, password: str):
        """
        验证用户身份。

        :param fake_db: 模拟的用户数据库。
        :param username: 用户名。
        :param password: 明文密码。
        :return: 如果验证成功，返回用户对象；否则返回 False。
        """
        user = UserDao.select_by_name( username)
        # 验证明文密码是否与已哈希的密码匹配
        if not user or not pwd_context.verify(password, user.hashed_password):
            return False
        return user


    async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
        """
        获取当前用户信息。

        :param token: Bearer 令牌。
        :return: 当前用户对象。
        :raises HTTPException: 如果无法验证凭据或用户不存在。
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            # decode 解码token内容
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except InvalidTokenError:
            raise credentials_exception
        user = get_user(fake_users_db, username=token_data.username)
        if user is None:
            raise credentials_exception
        return user


    async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)],
    ):
        if current_user.disabled:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user

    
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