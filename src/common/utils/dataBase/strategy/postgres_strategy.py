from common.utils.dataBase.interface.db_interface import DBInterface


class PostgresStrategy(DBInterface):
    """
        策略模式组装postgres作为基础的服务端数据库
    """
    """
    Strategy pattern implementation for PostgreSQL database
    Supports relational, vector (via pgvector), and graph (via Apache AGE) operations
    """
    
   