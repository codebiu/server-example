from sqlmodel import Column, DateTime, Field, SQLModel
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
    id: str = Field(
        default_factory=lambda: uuid4().hex,
        primary_key=True,
        index=True,
        unique=True,
        description="文章的唯一标识符",
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True,
        ),
        default_factory=datetime.now,  # 动态生成当前时间
        description="文章的创建时间",
    )
    update_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True,
        ),
        default_factory=datetime.now,  # 首次创建时等于 created_at
        description="文章的最后更新时间",
    )


class ArticleUpdate(SQLModel):
    # 仅包含可更新字段，避免覆盖 created_at
    title: str | None = None
    content: str | None = None
    category: str | None = None
    tags: str | None = None
    is_published: bool | None = None
    update_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True,
        ),
        default_factory=datetime.now,
    )  # 动态更新时间


class ArticlePublic(ArticleBase):
    id: str
    created_at: datetime
    update_at: datetime | None
