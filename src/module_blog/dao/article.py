from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

# self
from config.db import Data, DataNoCommit
from ..do.article import Article, ArticleUpdate


class ArticleDao:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, article: Article) -> str:
        self.session.add(article)
        await self.session.flush()
        return article.id

    async def delete(self, id: str) -> None:
        article = await self.session.get(Article, id)
        if article:
            await self.session.delete(article)

    async def update(self, id: str, article_update: ArticleUpdate) -> Optional[Article]:
        article = await self.session.get(Article, id)
        if article:
            for key, value in article_update.dict(exclude_unset=True).items():
                setattr(article, key, value)
            self.session.add(article)
        return article


    async def select(self, id: str) -> Article | None:
        return await self.session.get(Article, id)

    async def list(self) -> list[Article]:
        result = await self.session.exec(select(Article))
        articles = result.all()
        return articles
