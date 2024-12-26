"""
    fastapi 基础配置
    fastapi base config
"""

# self
from config.log import console
from utils.dataBase.DataBaseSqlite import DataBaseSqlite
from config.path import path_base
from config.index import conf

# lib
from functools import wraps
from sqlalchemy.ext.asyncio.engine import AsyncEngine


database = conf["database"]
# ###################################关系数据库#############################
# sqlite路径
sqlite = database["sqlite"]
SQLALCHEMY_DATABASE_URL = sqlite["path"]
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

console.log("...关系数据库配置完成")
