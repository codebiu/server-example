# self
from do.user import User,UserCreate
from dao.user import UserDao

# lib


class UsersService:
    """user"""

    @staticmethod
    async def add(user: UserCreate)->str:
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
    async def list() -> list[User]:
        return await UserDao.list()
