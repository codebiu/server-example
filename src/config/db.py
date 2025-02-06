"""
    FastAPI 基础配置
    FastAPI Base Config
"""

# 第三方库导入
from functools import wraps
from typing import Callable, Any, Coroutine

# 项目模块导入
from config.log import logger
from utils.dataBase.DataBaseSqlite import DataBaseSqlite
from config.index import conf

# ################################### 关系型数据库配置 #############################

# 数据库配置获取
database_config = conf["database"]["sqlite"]
SQLALCHEMY_DATABASE_URL = database_config["path"]

# 初始化SQLite数据库连接
database_sqlite_default = DataBaseSqlite(SQLALCHEMY_DATABASE_URL)
database_sqlite_default.connect()

# 数据库引擎与会话工厂
engine = database_sqlite_default.engine
session_factory = database_sqlite_default.sessionLocal

logger.debug("...关系型数据库配置完成")

# ################################### 数据库会话装饰器 #############################

def db_session(commit: bool = True) -> Callable[[Callable], Callable[[Any], Coroutine]]:
    """
    数据库会话装饰器工厂
    :param commit: 是否自动提交事务
    """
    def decorator(func: Callable) -> Callable[[Any], Coroutine]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            async with session_factory() as session:
                try:
                    kwargs["session"] = session
                    result = await func(*args, **kwargs)
                    if commit:
                        await session.commit()
                        console.debug("事务已提交")
                    return result
                except Exception as e:
                    console.error(f"数据库操作异常: {str(e)}")
                    await session.rollback()
                    console.debug("事务已回滚")
                    raise
        return wrapper
    return decorator

# 快捷装饰器定义
Data = db_session(commit=True)
DataNoCommit = db_session(commit=False)