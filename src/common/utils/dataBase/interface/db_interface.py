# baselib
from abc import ABC, abstractmethod

class DBInterface(ABC):
    """
    数据库接口

    定义了所有数据库操作类需要遵循的基本接口契约。
    任何继承自此类的具体数据库实现都必须实现所有标记为 @abstractmethod 的方法。
    """

    @abstractmethod
    def __init__(self):
        """
        初始化方法。

        子类必须实现此方法，通常用于接收数据库连接所需的配置参数
        （例如：主机地址、端口、用户名、密码、数据库名等）。
        由于是抽象方法，基类中不提供具体实现。
        """
        raise NotImplementedError("子类必须实现 __init__ 方法")

    @abstractmethod
    def connect(self):
        """
        建立数据库连接。

        子类需要实现具体的数据库连接逻辑。
        """
        raise NotImplementedError("子类必须实现 connect 方法")

    @abstractmethod
    def is_connected(self):
        """
        检查当前数据库连接状态。

        子类需要实现检查连接是否有效、活动的逻辑。
        :return: 如果连接有效则返回 True，否则返回 False。
        """
        raise NotImplementedError("子类必须实现 is_connected 方法")

    @abstractmethod
    def reconnect(self):
        """
        重新连接数据库。

        通常在连接丢失或需要刷新连接时调用。
        子类需要实现断开现有连接（如果需要）并重新建立连接的逻辑。
        """
        raise NotImplementedError("子类必须实现 reconnect 方法")

    @abstractmethod
    def disconnect(self):
        """
        断开数据库连接。

        子类需要实现关闭数据库连接并释放相关资源的逻辑。
        """
        raise NotImplementedError("子类必须实现 disconnect 方法")

    @abstractmethod
    def get_info(self):
        """
        获取数据库相关信息。

        例如：数据库版本、服务器状态、连接参数等。
        子类需要实现获取其特定数据库信息的逻辑。
        :return: 包含数据库信息的字典或其他合适的数据结构。
        """
        raise NotImplementedError("子类必须实现 get_info 方法")