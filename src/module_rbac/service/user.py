# self
from module_main.do.user import User,User, UserLogin
from module_main.dao.user import UserDao

# lib


class UserService:
    """user"""

    @staticmethod
    async def add(user: User)->str:
        return await UserDao.add(user)

    @staticmethod
    async def delete(id: str):
        await UserDao.delete(id)

    @staticmethod
    async def update(user: User):
        await UserDao.update(user)

    @staticmethod
    async def select(id: str) -> User | None:
        return await UserDao.select(id)
    @staticmethod
    async def select_by_email(email: str) -> User | None:
        return await UserDao.select_by_email(email)
    @staticmethod
    async def select_by_tel(tel: str) -> User | None:
        return await UserDao.select_by_tel(tel)
    
    @staticmethod
    async def list() -> list[User]:
        return await UserDao.list()
