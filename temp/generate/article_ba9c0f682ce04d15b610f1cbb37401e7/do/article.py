from sqlmodel import Field, SQLModel
from uuid import uuid4
from datetime import datetime


class ArticleBase(SQLModel):
    id: int
    title: str
    content: str
    author_id: int
    category: str
    tags: list[str]
    created_at: datetime
    updated_at: datetime
    is_published: bool
    views: int
    slug: str


class Article(ArticleBase, table=True):
    """表结构"""
    
    # uuid 标准格式
    id: str = Field(
        default_factory=lambda: uuid4().hex, primary_key=True, index=True, unique=True
    )
    created_at: datetime = Field(default=datetime.now())
    update_at: datetime | None = None


class ArticleUpdate(ArticleBase):
    id: str
    update_at: datetime = Field(default=datetime.now())


class ArticlePublic:
    id: str
