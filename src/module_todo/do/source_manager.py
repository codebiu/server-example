# models.py
import uuid
from enum import Enum
from pathlib import Path
from dataclasses import dataclass
from pydantic import BaseModel, Field

class SourceType(str, Enum):
    """项目来源类型枚举"""

    ZIP = "zip"  # ZIP文件上传
    SVN = "svn"  # SVN仓库
    GIT = "git"  # Git仓库


@dataclass
class ZipSource(BaseModel):
    """ZIP文件来源配置"""
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)   


@dataclass
class SVNSource(BaseModel):
    """SVN仓库来源配置"""

    url: str  # 仓库地址
    username: str = None  # 用户名(可选)
    password: str = None  # 密码(可选)
    branch: str = None  # 分支(可选)
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)   


@dataclass
class GitSource(BaseModel):
    """Git仓库来源配置"""

    url: str  # 仓库地址
    branch: str = "main"  # 分支，默认main
    username: str = None  # 用户名(可选)
    token: str = None  # 访问令牌(可选)


