# self

from config.log import console
from config.fastapi_config import app
from service.index import TableService

# lib
from fastapi import APIRouter, status




# 基础db
router = APIRouter()

# 测试
@router.get("/create", status_code=status.HTTP_201_CREATED)
async def create():
    """创建未创建的表"""
    result = await TableService.create()
    return result


app.include_router(router, prefix="/db", tags=["db"])
console.log("...controller index")
