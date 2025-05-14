# self
from do.article import Article
from dao.article import UserDao

# lib


class UserService:
    """article"""

    @staticmethod
    async def add(article: Article)->str:
        return await UserDao.add(article)

    @staticmethod
    async def delete(id: str):
        await UserDao.delete(id)

    @staticmethod
    async def update(article: Article):
        await UserDao.update(article)

    @staticmethod
    async def select(id: str) -> Article | None:
        return await UserDao.select(id)
    @staticmethod
    async def select_by_email(email: str) -> Article | None:
        return await UserDao.select_by_email(email)
    @staticmethod
    async def select_by_tel(tel: str) -> Article | None:
        return await UserDao.select_by_tel(tel)
    
    @staticmethod
    async def list() -> list[Article]:
        return await UserDao.list()
