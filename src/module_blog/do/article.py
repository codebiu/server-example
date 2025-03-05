from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

from module_rbac.do.user import User

class Article(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    is_private: bool = Field(default=False)
    author_id: int = Field(foreign_key="user.id")
    author: User = Relationship(back_populates="articles")
    shared_users: List[User] = Relationship(back_populates="shared_articles", link_model="ArticleUser")
# 外键 foreign_key
class ArticleUser(SQLModel, table=True):
    article_id: int = Field(foreign_key="article.id", primary_key=True)
    user_id: int = Field(foreign_key="user.id", primary_key=True)