# # self
# # from config.log import logger
# from config.server import app
# from ..service.dict import DictService
# from module_main.do.dict import Dict, DictCreate, DictUpdate
# from common.utils.dataBase.DBEX import DBExtention, DBExtentiontentionBase

# # lib
# from fastapi.responses import JSONResponse
# from fastapi import APIRouter, HTTPException, Request, status

# router = APIRouter()

# DBExtention.controller_init(router, "dict", DictService, Dict, DictCreate, DictUpdate)

# app.include_router(router, prefix="/dict", tags=["字典"])

# # routerTest = APIRouter()

# # DBExtentiontentionBase.controller_init(routerTest, "test", DictService,Dict, DictCreate)

# # app.include_router(routerTest, prefix="/test", tags=["测试"])
