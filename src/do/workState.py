from sqlmodel import Field, SQLModel
from uuid import uuid4,UUID
from datetime import datetime

# 定义模型类，继承自基本类
class workState(SQLModel, table=True):
    '''面试记录列表 单个会议对象'''
    # 面试编号
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True, index=True, unique=True)
    # 面试模式
    mode: str
    # 音色
    voice: str
    # 语言
    language: str
    # 题量
    question_num: int
    # 等待时间
    wait_time: int
    
