


from enum import Enum

class DatabaseMode(Enum):
    # 嵌入式数据库 使用sqlite(包含插件sqlvec)和kuzu(图数据库)
    EMBEDDED = "sqlite_sqlvec_kuzu"
    # postgres(包含向量插件pgvector和图插件apache age)
    POSTGRES = "postgres_pgvector_apacheage"

class DatabaseAdapter:
    """统一数据库适配器（策略模式版）"""
    def __init__(self, mode: DatabaseMode, connection_params: dict[str, any]|None = None):
        self._strategy = self._create_strategy(mode)
        self._params = connection_params or {}

    def _create_strategy(self, mode: DatabaseMode) -> DatabaseStrategy:
        """工厂方法创建策略实例"""
        strategies = {
            DatabaseMode.EMBEDDED: EmbeddedStrategy,
            DatabaseMode.POSTGRES: PostgresStrategy
        }
        return strategies[mode]()

    async def connect(self) -> None:
        """建立数据库连接"""
        await self._strategy.connect(self._params)

    async def execute_sql_rel(self, query: str, *args) -> list[any]:
        """执行SQL查询"""
        return await self._strategy.execute_sql_rel(query, *args)

    async def execute_sql_vector(self, query: str, vector: list[float], top_k: int = 5) -> list[any]:
        """向量相似度搜索"""
        return await self._strategy.execute_sql_vector(query, vector, top_k)

    async def execute_sql_graph(self, cypher: str, **params) -> any:
        """图数据库查询"""
        return await self._strategy.execute_sql_graph(cypher, **params)

    async def close(self) -> None:
        """关闭连接"""
        await self._strategy.close()
if __name__ == '__main__':
    from config.index import conf
    from config.log import logger
    import asyncio
    async def main():
        database_config = conf["database"].get("postgresql")
        database_sqlite_default = DataBasePostgre(
            database_config["user"],
            database_config["password"],
            database_config["host"],
            database_config["port"],
            database_config["database"],
        )
        # Postgres使用
        pg_adapter = DatabaseAdapter(
            DatabaseMode.POSTGRES,
            database_config
        )
        await pg_adapter.connect()
    
    # 异步运行

    asyncio.run(main())