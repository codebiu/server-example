# self
from config.log import console
from config.fastapi_config import app
from dao.index import TableDao
# lib
from fastapi import HTTPException

class TableService:
    # 更新数据库 静态方法
    @staticmethod
    async def create():
        console.log('test')
        try:
            # 调用函数
            await TableDao.create()
            return HTTPException(status_code=200, detail={"message": "update table success"})
        except Exception as e:
            raise HTTPException(status_code=500, detail=e)