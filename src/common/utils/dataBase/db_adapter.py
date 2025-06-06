# 根据配置选用嵌入式和bs数据库
# 当前考虑:关系数据库 向量数据库 图数据库
# @代指插件模式数据库本体@插件)
# 嵌入式: sqlite sqlite@sqlvec kuzu
# bs数据库: postgres postgres@pgvector postgres@apacheage

from enum import Enum

from common.utils.dataBase.interface.db_interface import DBInterface
from common.utils.dataBase.strategy.postgres_strategy import PostgresStrategy

class DBMode(Enum):
    # 嵌入式数据库 使用sqlite(包含插件sqlvec)和kuzu(图数据库)
    EMBEDDED = "sqlite_sqlite@sqlvec_kuzu"
    # postgres(包含向量插件pgvector和图插件apache age)
    POSTGRES = "postgres_postgres@pgvector_postgres@apacheage"

class DBAdapter:
    """统一数据库适配器"""
    def __init__(self, mode: DBMode, connection_params: dict[str, any]|None = None):
        self._strategy:DBInterface = self._create_strategy(mode)
        self._params = connection_params or {}

    def _create_strategy(self, mode: DBMode) -> DBInterface:
        """工厂方法创建策略实例"""
        strategies = {
            # DBMode.EMBEDDED: EmbeddedStrategy,
            DBMode.POSTGRES: PostgresStrategy
        }
        return strategies[mode]()

    async def connect(self) -> None:
        """建立数据库连接"""
        await self._strategy.connect(self._params)

    async def exec_base(self, query: str, *args) -> list[any]:
        """执行SQL查询"""
        return await self._strategy.exec_base(query, *args)

    async def exec_vector(self, query: str, vector: list[float], top_k: int = 5) -> list[any]:
        """向量相似度搜索"""
        return await self._strategy.exec_vector(query, vector, top_k)

    async def exec_graph(self, cypher: str, **params) -> any:
        """图数据库查询"""
        return await self._strategy.exec_graph(cypher, **params)

    async def close(self) -> None:
        """关闭连接"""
        await self._strategy.close()
if __name__ == '__main__':
    from config.index import conf
    from config.log import logger
    import asyncio
    async def main():
        database_config = conf["database.postgresql"]
        # Postgres使用
        pg_adapter = DBAdapter(
            DBMode.POSTGRES,
            database_config
        )
        await pg_adapter.connect()
    
    # 异步运行

    asyncio.run(main())