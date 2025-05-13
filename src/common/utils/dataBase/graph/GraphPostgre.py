from typing import TypeVar, Generic, Optional, List, Dict, Any, Union
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import json

T = TypeVar("T", bound="GraphModel")


class GraphModel(BaseModel):
    """图数据模型基类"""

    id: Optional[int] = None
    label: str
    properties: Dict[str, Any] = {}

    class Config:
        arbitrary_types_allowed = True


class DataBaseGraphPostgre:
    def __init__(self, session: AsyncSession, graph_name: str = "my_graph"):
        self.session = session
        self.graph_name = graph_name

    # 查看有哪些图 SELECT * FROM ag_catalog.ag_graph;
    async def list_graphs(self) -> List[str]:
        """列出所有图
        return :["my_graph", "graph2", "graph3"...]
        """
        result = await self.session.execute(text("SELECT * FROM ag_catalog.ag_graph"))
        result_list = [row[1] for row in result.all()]
        return result_list

    # 图管理功能
    async def create_graph(self) -> bool:
        """创建新图"""
        await self.session.execute(
            text("SELECT ag_catalog.create_graph(:graph_name)"),
            {"graph_name": self.graph_name},
        )
        await self.session.commit()
        return True

    async def drop_graph(self, cascade: bool = False) -> bool:
        """删除当前图
        cascade: 是否级联删除

        """
        query = "SELECT ag_catalog.drop_graph(:graph_name, :cascade)"
        await self.session.execute(
            text(query), {"graph_name": self.graph_name, "cascade": cascade}
        )
        await self.session.commit()
        return True

    async def graph_exists(self) -> bool:
        """检查当前图是否存在"""
        result = await self.session.execute(
            text("SELECT 1 FROM ag_catalog.ag_graph WHERE name = :graph_name"),
            {"graph_name": self.graph_name},
        )
        return result.scalar() is not None

    async def create_node(self, element: T) -> T:
        """创建顶点"""
        query = text(
            f"""
            SELECT * FROM ag_catalog.cypher('my_graph', $$
                CREATE (v:{element.label} {{name: 'Andres', title: 'Developer'}})
            $$) as (n ag_catalog.agtype);
        """
        )
        params = {"props": element.properties}

        result = await self.session.execute(query)
        row = result.one()
        element.id = json.loads(row.id)
        return element


if __name__ == "__main__":
    from common.utils.dataBase.DataBasePostgre import DataBasePostgre
    from config.index import conf
    from config.log import logger

    # 定义数据模型
    class Person(GraphModel):
        label: str = "Person"

    class Knows(GraphModel):
        label: str = "KNOWS"
        start_id: int
        end_id: int

    # 使用ORM
    async def main():
        # 创建异步引擎和会话
        database_config = conf["database"].get("postgresql")
        database_sqlite_default = DataBasePostgre(
            database_config["user"],
            database_config["password"],
            database_config["host"],
            database_config["port"],
            database_config["database"],
        )
        database_sqlite_default.connect()
        engine = database_sqlite_default.engine
        session = database_sqlite_default.sessionFactory()
        orm = GraphPostgre(session)

        try:
            # 检查图是否存在，不存在则创建
            if not await orm.graph_exists():
                await orm.create_graph()
                logger.info(f"Created graph '{orm.graph_name}'")
            graph_name_list = await orm.list_graphs()
            logger.info(f"Graphs: {graph_name_list}")
            # # 创建顶点
            alice = Person(properties={"name": "Alice", "age": 30})
            alice = await orm.create_node(alice)
            logger.info(f"Created Alice with ID: {alice.id}")
            # # 删除图
            # await orm.drop_graph(True)

        finally:
            await session.close()
            await engine.dispose()

    # 运行异步主函数
    import asyncio

    asyncio.run(main())
