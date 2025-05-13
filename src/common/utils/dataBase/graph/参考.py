from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Dict, Any, List, Protocol
import json

class DatabaseMode(Enum):
    """数据库模式枚举"""
    EMBEDDED = "sqlite_sqlvec_kuzu"
    POSTGRES = "postgres_pgvector_apacheage"

class SQLExecutor(Protocol):
    """SQL执行接口"""
    async def execute(self, query: str, *args) -> List[Any]:
        """执行SQL查询"""
        ...

    async def close(self) -> None:
        """关闭连接"""
        ...

class VectorSearchEngine(Protocol):
    """向量搜索接口"""
    async def search(self, query: str, vector: List[float], top_k: int) -> List[Any]:
        """向量相似度搜索"""
        ...

    async def close(self) -> None:
        """关闭连接"""
        ...

class GraphQueryEngine(Protocol):
    """图查询接口"""
    async def query(self, cypher: str, **params) -> Any:
        """执行图查询"""
        ...

    async def close(self) -> None:
        """关闭连接"""
        ...

# SQL执行实现
class SQLiteExecutor:
    def __init__(self):
        self._conn = None

    async def connect(self, params: Dict[str, Any]) -> None:
        import aiosqlite
        self._conn = await aiosqlite.connect(params.get('db_path', ':memory:'))
        await self._conn.enable_load_extension(True)
        await self._conn.load_extension('sqlvec')

    async def execute(self, query: str, *args) -> List[Any]:
        cursor = await self._conn.execute(query, args)
        return await cursor.fetchall()

    async def close(self) -> None:
        if self._conn:
            await self._conn.close()

class PostgresExecutor:
    def __init__(self):
        self._pool = None

    async def connect(self, params: Dict[str, Any]) -> None:
        import asyncpg
        self._pool = await asyncpg.create_pool(
            host=params.get('host', 'localhost'),
            port=params.get('port', 5432),
            user=params.get('user'),
            password=params.get('password'),
            database=params.get('database')
        )

    async def execute(self, query: str, *args) -> List[Any]:
        async with self._pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def close(self) -> None:
        if self._pool:
            await self._pool.close()

# 向量搜索实现
class SQLiteVectorSearch:
    def __init__(self, sql_executor: SQLExecutor):
        self._sql_executor = sql_executor

    async def search(self, query: str, vector: List[float], top_k: int) -> List[Any]:
        sql = f"SELECT * FROM ({query}) ORDER BY vec_distance(embedding, ?) LIMIT ?"
        return await self._sql_executor.execute(sql, vector, top_k)

    async def close(self) -> None:
        await self._sql_executor.close()

class PostgresVectorSearch:
    def __init__(self, sql_executor: SQLExecutor):
        self._sql_executor = sql_executor

    async def search(self, query: str, vector: List[float], top_k: int) -> List[Any]:
        sql = f"{query} ORDER BY embedding <-> $1 LIMIT $2"
        return await self._sql_executor.execute(sql, vector, top_k)

    async def close(self) -> None:
        await self._sql_executor.close()

# 图查询实现
class KuzuGraphQuery:
    def __init__(self):
        self._db = None

    async def connect(self, params: Dict[str, Any]) -> None:
        import kuzu
        self._db = kuzu.database(params.get('kuzu_path', 'kuzu_data'))

    async def query(self, cypher: str, **params) -> Any:
        conn = self._db.connect()
        result = conn.execute(cypher, params)
        return result.get_as_df()

    async def close(self) -> None:
        if self._db:
            self._db.close()

class PostgresGraphQuery:
    def __init__(self, sql_executor: SQLExecutor):
        self._sql_executor = sql_executor
        self._database = None

    async def connect(self, params: Dict[str, Any]) -> None:
        self._database = params.get('database')

    async def query(self, cypher: str, **params) -> Any:
        query = "SELECT * FROM ag_catalog.cypher($1, $2)"
        params_str = f"{cypher} {json.dumps(params)}"
        return await self._sql_executor.execute(query, self._database, params_str)

    async def close(self) -> None:
        await self._sql_executor.close()

# 数据库适配器主类
class DatabaseAdapter:
    def __init__(
        self,
        sql_executor: SQLExecutor,
        vector_engine: Optional[VectorSearchEngine] = None,
        graph_engine: Optional[GraphQueryEngine] = None
    ):
        self._sql_executor = sql_executor
        self._vector_engine = vector_engine
        self._graph_engine = graph_engine

    async def connect(self, params: Dict[str, Any]) -> None:
        """建立所有组件的连接"""
        await self._sql_executor.connect(params)
        if self._vector_engine and hasattr(self._vector_engine, 'connect'):
            await self._vector_engine.connect(params)
        if self._graph_engine and hasattr(self._graph_engine, 'connect'):
            await self._graph_engine.connect(params)

    async def execute_sql(self, query: str, *args) -> List[Any]:
        """执行SQL查询"""
        return await self._sql_executor.execute(query, *args)

    async def vector_search(self, query: str, vector: List[float], top_k: int = 5) -> List[Any]:
        """向量相似度搜索"""
        if not self._vector_engine:
            raise NotImplementedError("Vector search not supported")
        return await self._vector_engine.search(query, vector, top_k)

    async def graph_query(self, cypher: str, **params) -> Any:
        """图数据库查询"""
        if not self._graph_engine:
            raise NotImplementedError("Graph query not supported")
        return await self._graph_engine.query(cypher, **params)

    async def close(self) -> None:
        """关闭所有连接"""
        await self._sql_executor.close()
        if self._vector_engine:
            await self._vector_engine.close()
        if self._graph_engine:
            await self._graph_engine.close()

# 工厂函数
def create_database_adapter(mode: DatabaseMode, connection_params: Dict[str, Any]) -> DatabaseAdapter:
    """创建数据库适配器实例"""
    if mode == DatabaseMode.EMBEDDED:
        sql_executor = SQLiteExecutor()
        vector_engine = SQLiteVectorSearch(sql_executor)
        graph_engine = KuzuGraphQuery()
        return DatabaseAdapter(sql_executor, vector_engine, graph_engine)
    
    elif mode == DatabaseMode.POSTGRES:
        sql_executor = PostgresExecutor()
        vector_engine = PostgresVectorSearch(sql_executor)
        graph_engine = PostgresGraphQuery(sql_executor)
        return DatabaseAdapter(sql_executor, vector_engine, graph_engine)
    
    raise ValueError(f"Unsupported database mode: {mode}")