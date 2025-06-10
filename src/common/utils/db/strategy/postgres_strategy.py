from common.utils.db.interface.db_interface import DBInterface


class PostgresStrategy(DBInterface):
    """
        策略模式组装postgres作为基础的服务端数据库
    """
    """
    Strategy pattern implementation for PostgreSQL database
    Supports relational, vector (via pgvector), and graph (via Apache AGE) operations
    """
    async def connect(self) -> None:
        """建立数据库连接"""
        await self.connect(self._params)

    async def exec_base(self, query: str, *args) -> list[any]:
        """执行SQL查询"""
        return await self.exec_base(query, *args)

    async def exec_vector(self, query: str, vector: list[float], top_k: int = 5) -> list[any]:
        """向量相似度搜索"""
        return await self.exec_vector(query, vector, top_k)

    async def exec_graph(self, cypher: str, **params) -> any:
        """图数据库查询"""
        return await self._strategy.exec_graph(cypher, **params)

    async def close(self) -> None:
        """关闭连接"""
        
        
        await self._strategy.close()
    
   