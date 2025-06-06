"""
FastAPI 基础配置
FastAPI Base Config
"""

# 第三方库导入
from functools import wraps
from typing import Callable, Any, Coroutine, Optional
from contextlib import asynccontextmanager
from sqlmodel.ext.asyncio.session import AsyncSession
# 项目模块导入
from config.log import logger
from config.index import conf

# ################################### 关系型数据库配置 #############################
#  todo @Transactional   ContextVar单次请求统一会话  与连接池关系

# 数据库配置获取
def get_database()-> DataBaseInterface:
    if conf["database"].get("sqlite"):
        database_config = conf["database"].get("sqlite")
        return DataBaseSqlite(database_config["path"])
    elif conf["database"].get("postgresql"):
        database_config = conf["database"].get("postgresql")        
        return DataBasePostgre(
            database_config["user"],
            database_config["password"],
            database_config["host"],
            database_config["port"],
            database_config["database"]
        )


# 初始化SQLite数据库连接
database_sqlite_default = get_database()
database_sqlite_default.connect()

# 数据库引擎与会话工厂
engine = database_sqlite_default.engine
session_factory = database_sqlite_default.sessionFactory

logger.info("ok...关系型数据库配置")

# 不主动处理事务，由Service层完全控制
@asynccontextmanager
async def get_db_session():
    """
    完整托管会话：自动处理事务和连接生命周期
    """
    async with session_factory() as session:  # 自动调用 __aenter__
        async with session.begin():           # 自动事务管理
            yield session

####################################### 注入模式 ###################################
