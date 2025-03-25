from sqlmodel import Field, SQLModel
from uuid import uuid4
from datetime import datetime


class ArticleBase(SQLModel):
    title: str = Field(description="文章的标题")
    content: str = Field(description="文章的内容")
    author_id: int = Field(description="作者的用户ID")
    category: str = Field(description="文章的分类")
    tags: str = Field(description="文章的标签（列表形式 ，号分割）")
    is_published: bool = Field(description="文章是否已发布")
    views: int = Field(description="文章的浏览量")
    slug: str = Field(description="文章的URL友好标识（用于SEO）")


class Article(ArticleBase, table=True):
    """表结构"""
    
    # uuid 标准格式
    id: str = Field(
        default_factory=lambda: uuid4().hex, primary_key=True, index=True, unique=True,description="文章的唯一标识符")
    created_at: datetime = Field(default=datetime.now(),description="文章的创建时间")
    update_at: datetime | None = Field(description="文章的最后更新时间")


class ArticleUpdate(ArticleBase):
    id: str
    update_at: datetime = Field(default=datetime.now())


class ArticlePublic:
    id: str
