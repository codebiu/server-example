# self
from ..do.article import Article
from ..dao.article import ArticleDao

# lib


class ArticleService:
    """article"""

    @staticmethod
    async def add(article: Article)->str:
        return await ArticleDao.add(article)

    @staticmethod
    async def delete(id: str):
        await ArticleDao.delete(id)

    @staticmethod
    async def update(article: Article):
        await ArticleDao.update(article)

    @staticmethod
    async def select(id: str) -> Article | None:
        return await ArticleDao.select(id)
    @staticmethod
    async def select_by_email(email: str) -> Article | None:
        return await ArticleDao.select_by_email(email)
    @staticmethod
    async def select_by_tel(tel: str) -> Article | None:
        return await ArticleDao.select_by_tel(tel)
    
    @staticmethod
    async def list() -> list[Article]:
        return await ArticleDao.list()
