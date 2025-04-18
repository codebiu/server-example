from abc import ABC, abstractmethod


class DBRelationInterface(ABC):
    """关系型数据库抽象基类"""

    @abstractmethod
    def get_session(self):
        pass

    @abstractmethod
    def create_all(self, models: list) -> None:
        pass