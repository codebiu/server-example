from sqlmodel import Field, SQLModel
from uuid import uuid4
from datetime import datetime


class DictBase(SQLModel):
    """字典表基础模型"""
    key: str = Field(description="字典键", max_length=100, index=True)
    value: str = Field(description="字典值", max_length=255)
    # type: str = Field(default="default", description="字典类型", max_length=50)
    # description: str = Field(default="", description="字典描述", max_length=255)
    # sort: int = Field(default=0, description="排序字段")
    # status: int = Field(default=1, description="状态: 0-禁用 1-启用")
    # is_system: bool = Field(default=False, description="是否系统字典")
    # is_deleted: bool = Field(default=False, description="是否已删除")


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


class DictPublic(DictBase):
    """字典表公开模型"""
    id: str
    created_at: datetime
    update_at: datetime | None
