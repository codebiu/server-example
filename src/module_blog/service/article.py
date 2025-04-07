# self
from contextlib import contextmanager
from ..do.article import Article
from ..dao.article import ArticleDao
from sqlmodel.ext.asyncio.session import AsyncSession
# lib


class ArticleService:
    """article"""
    def __init__(self, session: AsyncSession):
        self.articleDao = ArticleDao(session)
        # self.user_dao = UserDAO(session)
        
    @contextmanager
    def transaction(self):
        """服务层事务管理"""
        try:
            yield
            self.dao.session.commit()
        except Exception:
            self.dao.session.rollback()
            raise

    async def add(self,article: Article)->str:
        return await self.articleDao.add(article)


    async def delete(self,id: str):
        await self.articleDao.delete(id)


    async def update(self,article: Article):
        await self.articleDao.update(article)


    async def select(self,id: str) -> Article | None:
        return await self.articleDao.select(id)

    async def select_by_email(self,email: str) -> Article | None:
        return await self.articleDao.select_by_email(email)

    async def select_by_tel(self,tel: str) -> Article | None:
        return await self.articleDao.select_by_tel(tel)
    
    async def list(self) -> list[Article]:
        return await self.articleDao.list()


# 新增的依赖项工厂函数
def get_service(session: AsyncSession = Depends(get_db)) -> ArticleService:
    return ArticleService(session)