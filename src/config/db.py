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
async def get_db_session() -> AsyncIterator[AsyncSession]:
    """
    完整托管会话：自动处理事务和连接生命周期
    """
    async with session_factory() as session:  # 自动调用 __aenter__
        async with session.begin():           # 自动事务管理
            yield session

####################################### 注入模式 ###################################


T = TypeVar('T')
def Dao(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
    """
    改进版自动事务装饰器（使用async with管理会话）：
    1. 支持嵌套事务
    2. 自动检测是否需要提交
    3. 支持手动控制事务
    4. 使用async with确保资源释放
    """
    @wraps(func)
    async def wrapper(self, *args, **kwargs) -> T:
        # 检查是否已有有效会话
        existing_session: Optional[AsyncSession] = getattr(self, 'session', None)
        
        if existing_session and isinstance(existing_session, AsyncSession) and existing_session.is_active:
            # 使用现有会话
            return await func(self, *args, **kwargs)
        else:
            # 创建新会话并管理其生命周期
            async with session_factory() as session:
                setattr(self, 'session', session)
                try:
                    async with session.begin():
                        result = await func(self, *args, **kwargs)
                        return result
                except Exception as e:
                    logger.error(f"数据库操作失败: {e}", exc_info=True)
                    if session.in_transaction():
                        await session.rollback()
                    raise
                finally:
                    delattr(self, 'session')  # 清理会话引用
    
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