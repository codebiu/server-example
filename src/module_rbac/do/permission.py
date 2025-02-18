# models/permission.py
from sqlmodel import SQLModel, Field

class Permission(SQLModel, table=True):
    """
    权限数据模型
    - id: 主键
    - name: 权限名称（唯一）
    - description: 权限描述
    """
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True, description="权限名称")
    description: str = Field(default="", description="权限描述")