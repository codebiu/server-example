from pydantic import BaseModel
from sqlmodel import Field, SQLModel
from uuid import uuid4
from datetime import datetime


class UserBase(SQLModel):
    name: str
    email: str


class User(UserBase, table=True):
    """表结构"""

    # uuid 标准格式
    id: str = Field(
        default_factory=lambda: uuid4().hex, primary_key=True, index=True, unique=True
    )
    created_at: datetime = Field(default=datetime.now())
    update_at: datetime | None = None
    # pwd
    pwd: str | None = None


class UserUpdate(UserBase):
    id: str
    # pwd
    pwd: str | None = None
    update_at: datetime = Field(default=datetime.now())





class UserPublic:
    id: str
# BaseModel
class UserCreate(BaseModel):
    email: str
    pwd: str | None = None
    
    
class UserLogin(BaseModel):
    """用于验证用户名和密码的模型"""
    email: str
    pwd: str
