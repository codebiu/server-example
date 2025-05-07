from abc import ABC, abstractmethod


class DBRelationInterface(ABC):
    """关系型数据库抽象基类"""
    
    @abstractmethod
    def get_session(self):
        pass

    @abstractmethod
    def create_all(self, models: list) -> None:
        pass

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    async def execute(self, sql: str, params: dict | None = None):
        """通用SQL执行函数"""
        pass
