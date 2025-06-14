"""
    fastapi 基础配置
    fastapi base config
"""

# self
from typing import Union

from pydantic import BaseModel
from config.log import logger
from config.index import conf

# lib
from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

import time

from common.utils.security.TokenUtil import TokenUtil

app = FastAPI(
    title="python工程模板",
    description="python工程模板",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    # 允许跨域的源列表，例如 ["http://www.example.org"] 等等，["*"] 表示允许任何源
    allow_origins=["*"],
    # 跨域请求是否支持 cookie，默认是 False，如果为 True，allow_origins 必须为具体的源，不可以是 ["*"]
    allow_credentials=False,
    # 允许跨域请求的 HTTP 方法列表，默认是 ["GET"]
    allow_methods=["*"],
    # 允许跨域请求的 HTTP 请求头列表，默认是 []，可以使用 ["*"] 表示允许所有的请求头
    # 当然 Accept、Accept-Language、Content-Language 以及 Content-Type 总之被允许的
    allow_headers=["*"],
    # 可以被浏览器访问的响应头, 默认是 []，一般很少指定
    # expose_headers=["*"]
    # 设定浏览器缓存 CORS 响应的最长时间，单位是秒。默认为 600，一般也很少指定
    # max_age=1000
)
############################### middleware 中间件 ###############################

middleware = conf.get("middleware")
# !!!全局
if middleware:
    # 启用gzip 会导致流失效
    if middleware.get("gzip"):
        app.add_middleware(GZipMiddleware, minimum_size=1000)


# 为app增加接口处理耗时的响应头信息
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response: Response = await call_next(request)
    await dealToken(request, response)
    # X- 作为前缀代表专有自定义请求头
    response.headers["X-Process-Time"] = str((time.time() - start_time) * 1000)

    return response


############################### token通用过滤 ##############################################

security = conf.get("security")
token_util: TokenUtil = TokenUtil(
    security["secret"], security["algorithm"], security["expire"]
)
async def dealToken(request: Request, response: Response):
    # 解析出数据
    # data = token_util.token2data(request)

    # 验证用户存在
    return



logger.info("ok...server服务配置")
