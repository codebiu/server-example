from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

# self
from config.db import Data,DataNoCommit
from ..do.article import Article, ArticlePublic


class ArticleDao:

    @DataNoCommit
    async def add(article: Article, session=AsyncSession) -> str:
        """插入一个新的article"""
        db_article = Article.model_validate(article)
        session.add(db_article)
        await session.commit() 
        return db_article.id

    @Data
    async def delete(id: str, session=AsyncSession):
        hero = await session.get(Article, id)
        return await session.delete(hero)

    @Data
    async def update(article: Article, session=AsyncSession):
        """更新article信息"""
        article_to_upadte:Article = await session.get(Article, article.id)
        article_to_upadte.name = article.name
        article_to_upadte.email = article.email
        session.add(article_to_upadte)
        await session.commit()  # 提交事务
        session.refresh(article_to_upadte)
        return article_to_upadte

    @DataNoCommit
    async def select(id: str, session=AsyncSession) -> Article | None:
        return await session.get(Article, id)
    
    @DataNoCommit
    async def list(session=AsyncSession) -> list[Article]:
        result = await session.exec(select(Article))
        articles = result.all()
        return articles
