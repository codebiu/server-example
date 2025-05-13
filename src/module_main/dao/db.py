from config.log import logger
from config.db import engine
from sqlmodel import SQLModel

class TableDao:
    """
    数据库基础操作类
    提供与数据库表相关的CRUD操作
    """
    @staticmethod
    async def create():
        """
        创建所有未创建的数据库表
        
        返回:
            None
        """
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
    @staticmethod
    async def update():
        """
        更新所有数据库表

        返回:
            None
        """
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
            await conn.run_sync(SQLModel.metadata.create_all)
                    
class BaseDao:
    def test():
        return ''

logger.info('ok...dao_index')