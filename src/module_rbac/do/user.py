# models/user.py
from sqlmodel import SQLModel, Field, Relationship
from typing import List
from module_rbac.do.role import Role

class UserRoleLink(SQLModel, table=True):
    """
    用户-角色关联表
    - user_id: 外键，关联用户表
    - role_id: 外键，关联角色表
    """
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
    role_id: int | None = Field(default=None, foreign_key="role.id", primary_key=True)

class User(SQLModel, table=True):
    """
    用户数据模型
    - id: 主键
    - username: 用户名（唯一）
    - password: 密码（哈希值）
    - is_active: 用户是否激活
    - roles: 用户拥有的角色列表（多对多关系）
    """
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, description="用户名")
    password: str = Field(description="密码（哈希值）")
    is_active: bool = Field(default=True, description="用户是否激活")
    roles: List[Role] = Relationship(back_populates="users", link_model=UserRoleLink)