# self
from config.log import logger
from module_main.dao.db import TableDao
# lib
from fastapi import HTTPException

class TableService:
    """
    数据库表服务类
    提供与数据库表相关的操作
    """
    # 更新数据库 静态方法
    @staticmethod
    async def create():
        """
        创建所有未创建的数据库表
        
        返回:
            HTTPException: 成功返回200状态码，失败返回500状态码
        """
        logger.info('test')
        try:
            # 调用函数
            await TableDao.create()
            return HTTPException(status_code=200, detail={"message": "update table success"})
        except Exception as e:
            raise HTTPException(status_code=500, detail=e)
        
    # 更新数据库 静态方法
    @staticmethod
    async def update():
        """
        更新所有数据库表

        返回:
            HTTPException: 成功返回200状态码，失败返回500状态码
        """
        try:
            # 调用函数
            await TableDao.update()
            return HTTPException(status_code=200, detail={"message": "update table success"})
        except Exception as e:
            raise HTTPException(status_code=500, detail=e)