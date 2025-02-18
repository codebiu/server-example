# models/role.py
from sqlmodel import SQLModel, Field, Relationship
from typing import List
from module_rbac.do.permission import Permission

class RolePermissionLink(SQLModel, table=True):
    """
    角色-权限关联表
    - role_id: 外键，关联角色表
    - permission_id: 外键，关联权限表
    """
    role_id: int | None = Field(default=None, foreign_key="role.id", primary_key=True)
    permission_id: int | None = Field(default=None, foreign_key="permission.id", primary_key=True)

class Role(SQLModel, table=True):
    """
    角色数据模型
    - id: 主键
    - name: 角色名称（唯一）
    - description: 角色描述
    - permissions: 角色拥有的权限列表（多对多关系）
    """
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True, description="角色名称")
    description: str = Field(default="", description="角色描述")
    permissions: List[Permission] = Relationship(back_populates="roles", link_model=RolePermissionLink)