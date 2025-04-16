from abc import abstractmethod

from common.utils.dataBase.interface.db_interface import DBInterface


class DBGraphInterface(DBInterface):
    """关系型数据库抽象基类"""

    @abstractmethod
    def get_session(self):
        """获取数据库会话"""
        raise NotImplementedError

    @abstractmethod
    def create_graph(self, models: list) -> None:
        """创建图"""
        raise NotImplementedError
