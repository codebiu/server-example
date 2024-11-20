from config.log import console
from config.db import engine
from sqlmodel import SQLModel

class TableDao:
    '''数据库基础操作类'''
    async def create():
        '''创建所有未创建的表格'''
        async with engine.begin() as conn:
            # await conn.run_sync(SQLModel.metadata.drop_all)
            await conn.run_sync(SQLModel.metadata.create_all)
                    
class BaseDao:
    def test():
        return ''

console.log('...基础sql配置完成')