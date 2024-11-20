# self

from config.log import console

# lib
from functools import wraps

# from sqlalchemy import create_engine
# import aiosqlite # 依赖写全防止找不到
from sqlmodel import create_engine, Session
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker

# baselib
from abc import ABC, abstractmethod


# 数据接口类
class DataBaseInterface(ABC):
    @abstractmethod
    def __init__(self):
        raise NotImplementedError

    def connect(self):
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError


class DataBaseSqlite(DataBaseInterface):
    url: str = None
    engine: create_async_engine = None
    sessionLocal: sessionmaker = None

    def __init__(self, path: str):
        # 打包跟随程序
        type = "sqlite+aiosqlite"
        self.url = f"{type}:///{path}"

    def connect(self):
        # 控制台打印SQL
        self.engine = create_async_engine(self.url, echo=True)
        self.sessionLocal = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

    def disconnect(self):
        print("sqlite disconnect")


class DataBasePostgre(DataBaseInterface):
    url: str = None
    pwd: str = None
    host: str = None
    port: int = None
    engine: create_async_engine = None
    sessionLocal: sessionmaker = None

    def __init__(self, path: str, user: str, pwd: str, host: str, port: int):
        type = "postgresql+asyncpg"
        # postgresql+asyncpg://hero:heroPass123@0.0.0.0:5432/heroes_db
        self.url = f"{type}://{user}:{pwd}@{host}:{port}/{path}"
        # todo: mysql
        #  "mysql+pymysql://user:password@host:port/database"

    def connect(self):
        # 控制台打印SQL
        self.engine = create_async_engine(self.url, echo=True)
        self.sessionLocal = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

    def disconnect(self):
        print("postgresql disconnect")


SQLALCHEMY_DATABASE_URL = "source/db/base.db"

dataBaseSqliteDeafault = DataBaseSqlite(SQLALCHEMY_DATABASE_URL)
dataBaseSqliteDeafault.connect()

# 当前数据引擎
engine: AsyncEngine = dataBaseSqliteDeafault.engine
sessionLocalUse = dataBaseSqliteDeafault.sessionLocal


def Data(f):
    """装饰器_负责创建执行和关闭"""

    @wraps(f)
    async def wrapper(*args, **kwargs):
        try:
            # 创建一个配置过的Session类
            async with sessionLocalUse() as session:  # 确保 session 总是被关闭
                # 设置session类型
                kwargs["session"] = session  # 将 session 作为关键字参数传递给 f
                result = await f(*args, **kwargs)
                await session.commit()  # 提交事务
                return result
        except Exception as e:
            # console.exception("数据库问题:"+str(e.orig))
            console.error("数据库问题:" + str(e))
            raise e

    return wrapper


def DataNoCommit(f):
    """装饰器_负责创建执行和关闭"""

    @wraps(f)
    async def wrapper(*args, **kwargs):
        try:
            # 创建一个配置过的Session类
            async with sessionLocalUse() as session:  # 确保 session 总是被关闭
                # 设置session类型
                kwargs["session"] = session  # 将 session 作为关键字参数传递给 f
                result = await f(*args, **kwargs)
                return result
        except Exception as e:
            # console.exception("数据库问题:"+str(e.orig))
            console.error("数据库问题:" + str(e))
            raise e

    return wrapper


# 管理器

console.log("...数据库配置完成")
