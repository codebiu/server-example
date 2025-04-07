from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

# self
from config.db import Data, DataNoCommit
from ..do.article import Article, ArticlePublic


class ArticleDao:
    def __init__(self, session: AsyncSession):
        self.session = self.session

    async def add(self, article: Article) -> str:
        """插入一个新的article"""
        db_article = Article.model_validate(article)
        self.session.add(db_article)
        await self.session.commit()
        return db_article.id

    async def delete(self, id: str):
        hero = await self.session.get(Article, id)
        return await self.session.delete(hero)

    async def update(self, article: Article):
        """更新article信息"""
        article_to_upadte: Article = await self.session.get(Article, article.id)
        article_to_upadte.name = article.name
        article_to_upadte.email = article.email
        self.session.add(article_to_upadte)
        await self.session.commit()  # 提交事务
        self.session.refresh(article_to_upadte)
        return article_to_upadte

    async def select(self, id: str) -> Article | None:
        return await self.session.get(Article, id)

    async def list(self) -> list[Article]:
        result = await self.session.exec(select(Article))
        articles = result.all()
        return articles
