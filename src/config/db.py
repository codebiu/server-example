"""
FastAPI 基础配置
FastAPI Base Config
"""

# 第三方库导入
from functools import wraps
from typing import Callable, Any, Coroutine

# 项目模块导入
from common.utils.dataBase.DataBasePostgre import DataBasePostgre
from common.utils.dataBase.DataBaseInterface import DataBaseInterface
from config.log import logger
from common.utils.dataBase.DataBaseSqlite import DataBaseSqlite
from config.index import conf

# ################################### 关系型数据库配置 #############################
#  todo @Transactional   ContextVar单次请求统一会话  与连接池关系

# 数据库配置获取
def get_database()-> DataBaseInterface:
    if conf["database"].get("sqlite"):
        database_config = conf["database"].get("sqlite")
        SQLALCHEMY_DATABASE_URL = database_config["path"]
        return DataBaseSqlite(SQLALCHEMY_DATABASE_URL)
    elif conf["database"].get("postgresql"):
        database_config = conf["database"].get("postgresql")
        SQLALCHEMY_DATABASE_HOST = database_config["host"]
        SQLALCHEMY_DATABASE_PORT = database_config["port"]
        SQLALCHEMY_DATABASE_USER = database_config["user"]
        SQLALCHEMY_DATABASE_PWD = database_config["password"]
        SQLALCHEMY_DATABASE_DATABASE = database_config["database"]
        
        return DataBasePostgre(
            SQLALCHEMY_DATABASE_USER,
            SQLALCHEMY_DATABASE_PWD,
            SQLALCHEMY_DATABASE_HOST,
            SQLALCHEMY_DATABASE_PORT,
            SQLALCHEMY_DATABASE_DATABASE
        )


# 初始化SQLite数据库连接
database_sqlite_default = get_database()
database_sqlite_default.connect()

# 数据库引擎与会话工厂
engine = database_sqlite_default.engine
session_factory = database_sqlite_default.sessionLocal

logger.info("ok...关系型数据库配置")

# ################################### 数据库会话装饰器 #############################


def db_session(commit: bool = True) -> Callable[[Callable], Callable[[Any], Coroutine]]:
    """
    数据库会话装饰器工厂
    :param commit: 是否自动提交事务
    """

    def decorator(func: Callable) -> Callable[[Any], Coroutine]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # 方便多事务统一处理 只有在没有传递 session 时才可以提交事务
            session = kwargs.get("session", None)
            should_commit = commit and session is None
            if session is None:
                async with session_factory() as session:
                    return await _execute_with_session(
                        func, session, should_commit, *args, **kwargs
                    )
            else:
                return await _execute_with_session(
                    func, session, should_commit, *args, **kwargs
                )

        return wrapper

    return decorator


async def _execute_with_session(
    func: Callable, session: Any, should_commit: bool, *args, **kwargs
) -> Any:
    """
    执行函数并处理事务提交或回滚
    """
    try:
        kwargs["session"] = session
        result = await func(*args, **kwargs)
        if should_commit:
            await session.commit()
            logger.info("事务已提交")
        return result
    except Exception as e:
        logger.error(f"数据库操作异常: {str(e)}")
        await session.rollback()
        logger.info("事务已回滚")
        raise


# 快捷装饰器定义
Data = db_session(commit=True)
DataNoCommit = db_session(commit=False)
