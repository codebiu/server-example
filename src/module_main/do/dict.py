from sqlmodel import Field, SQLModel
from uuid import uuid4
from datetime import datetime


class DictBase(SQLModel):
    key: str
    value: str


class Dict(DictBase, table=True):
    """表结构"""

    # uuid 标准格式
    id: str = Field(
        default_factory=lambda: uuid4().hex, primary_key=True, index=True, unique=True
    )
    created_at: datetime = Field(default=datetime.now())
    update_at: datetime | None = None


class DictUpdate(DictBase):
    id: str
    update_at: datetime = Field(default=datetime.now())


class DictCreate(DictBase):
    pass


class DictPublic:
    id: str
