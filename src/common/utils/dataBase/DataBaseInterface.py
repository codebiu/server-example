# baselib
from abc import ABC, abstractmethod


# 数据接口类
class DataBaseInterface(ABC):
    @abstractmethod
    def __init__(self):
        raise NotImplementedError

    def connect(self):
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError