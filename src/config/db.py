"""
FastAPI 基础配置
FastAPI Base Config
"""

# 第三方库导入
from functools import wraps
from typing import Callable, Any, Coroutine, Optional
from contextlib import asynccontextmanager
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import AsyncIterator
from typing import Callable, TypeVar, Any, Coroutine
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
session_factory = database_sqlite_default.sessionFactory

logger.info("ok...关系型数据库配置")

# 不主动处理事务，由Service层完全控制
@asynccontextmanager
async def get_db_session() -> AsyncIterator[AsyncSession]:
    """
    会话管理器：完全由Service层控制事务,仅作为会话生命周期入口
    """
    async with session_factory() as session:
        try:
            yield session
        finally:
            # 确保会话关闭，事务由Service层控制
            await session.close()

####################################### 注入模式 ###################################


T = TypeVar('T')

def auto_commit(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
    """
    增强版自动事务装饰器：
    1. 支持嵌套事务
    2. 自动检测是否需要提交
    3. 支持手动控制事务
    """
    @wraps(func)
    async def wrapper(self, *args, **kwargs) -> T:
        # 检查是否已有session
        session: Optional[AsyncSession] = getattr(self, 'session', None)
        is_new_session = False
        
        if session is None or not isinstance(session, AsyncSession) or not session.is_active:
            # 创建新session
            session = session_factory()
            setattr(self, 'session', session)
            is_new_session = True
            await session.__aenter__()
        
        try:
            result = await func(self, *args, **kwargs)
            
            # 只有是新session且没有活跃事务时才自动提交
            if is_new_session and not await session.in_transaction():
                await session.commit()
            
            return result
        except Exception as e:
            # 只有是新session时才回滚
            if is_new_session and await session.in_transaction():
                await session.rollback()
            raise
        finally:
            # 只有是新session时才关闭
            if is_new_session:
                await session.__aexit__(None, None, None)
    
    return wrapper

def transactional():
    """
    Service层事务装饰器
    """
    def decorator(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
        @wraps(func)
        async def wrapper(self, *args, **kwargs) -> T:
            # 检查是否已有session
            if not hasattr(self, 'session') or not isinstance(self.session, AsyncSession):
                async with session_factory() as session:
                    self.session = session
                    try:
                        result = await func(self, *args, **kwargs)
                        await session.commit()
                        return result
                    except Exception as e:
                        await session.rollback()
                        raise
            else:
                return await func(self, *args, **kwargs)
        return wrapper
    return decorator