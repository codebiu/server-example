# lib
import asyncio
import threading
import time
from config.fastapi_config import app
from fastapi import APIRouter, status

# self
from config.log import console
from config.fastapi_config import app

router = APIRouter()


thread1_a = 0


@router.get("/thread1", status_code=status.HTTP_201_CREATED, summary="test")
def thread1():
    # 循环100次
    global thread1_a
    thread1_a += 1
    b = thread1_a
    print(threading.current_thread(), "thread1")
    for i in range(10):
        # 等待一秒
        print(threading.current_thread(), b, "=========", i)
        time.sleep(5)

    return {"b": b}


thread2_a = 0


@router.get("/thread2", status_code=status.HTTP_201_CREATED, summary="test")
async def thread2():
    # 循环100次
    global thread2_a
    thread2_a += 1
    b = thread2_a
    print(threading.current_thread(), "thread2")
    for i in range(10):
        # 等待一秒异步
        print(threading.current_thread(), b, "=========", i)
        await asyncio.sleep(5)

    return {"thread2": "thread2"}


app.include_router(router, prefix="/test0", tags=["测试0"])
