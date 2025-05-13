from sqlmodel import Column, DateTime, Field, SQLModel
from uuid import uuid4
from datetime import datetime


class TestBase(SQLModel):
    content: str = Field(description="内容")


class Test(TestBase, table=True):
    id: str = Field(
        default_factory=lambda: uuid4().hex,
        primary_key=True,
        index=True,
        unique=True,
        description="唯一标识符",
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True,
        ),
        default_factory=datetime.now,  # 动态生成当前时间
        description="创建时间",
    )
    update_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True,
        ),
        default_factory=datetime.now,  # 首次创建时等于 created_at
        description="更新时间",
    )


class TestUpdate(SQLModel):
    content: str | None = None
    update_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True,
        ),
        default_factory=datetime.now,
    )  # 动态更新时间


class TestPublic(TestBase):
    id: str
    created_at: datetime
    update_at: datetime | None
