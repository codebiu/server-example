from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from pydantic import BaseModel

from module_blog.do.article import Article

app = FastAPI()

# 假设你已经有一个数据库引擎
from sqlmodel import create_engine

DATABASE_URL = "sqlite:///./blog.db"
engine = create_engine(DATABASE_URL)

# 依赖项，获取数据库会话
def get_db():
    with Session(engine) as session:
        yield session

# 用户认证（简化版）
def get_current_user(db, token):
    # 这里实现用户认证逻辑
    pass

# 文章创建
class ArticleCreate(BaseModel):
    title: str
    content: str
    is_private: bool = False
    shared_user_ids: List[int] = []

@app.post("/articles/", response_model=Article)
def create_article(article: ArticleCreate, db, current_user: User = Depends(get_current_user)):
    db_article = Article(**article.dict(), author_id=current_user.id)
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

# 获取文章
@app.get("/articles/{article_id}", response_model=Article)
def get_article(article_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    article = db.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    # !!!!!!!!!!! 验证用户是否有权限查看文章
    if article.is_private:
        if article.author_id != current_user.id and current_user.id not in [user.id for user in article.shared_users]:
            raise HTTPException(status_code=403, detail="Not authorized to view this article")
    
    return article

# 获取用户的所有文章
@app.get("/users/{user_id}/articles", response_model=List[Article])
def get_user_articles(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view these articles")
    
    return user.articles

# 其他路由和逻辑可以根据需要添加