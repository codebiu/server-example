from typing import TypeVar, Generic, Optional, List, Dict, Any, Union
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import json

T = TypeVar('T', bound='GraphModel')

class GraphModel(BaseModel):
    """图数据模型基类"""
    id: Optional[int] = None
    label: str
    properties: Dict[str, Any] = {}
    
    class Config:
        arbitrary_types_allowed = True

class GraphPostgre:
    def __init__(self, session: AsyncSession, graph_name: str = "my_graph"):
        self.session = session
        self.graph_name = graph_name
    
    async def create(self, element: T) -> T:
        """创建顶点或边"""
        if hasattr(element, 'start_id'):  # 边类型
            query = text(f"""
                SELECT * FROM cypher(:graph_name, $$
                    MATCH (a), (b)
                    WHERE id(a) = $start_id AND id(b) = $end_id
                    CREATE (a)-[r:{element.label} $props]->(b)
                    RETURN id(r) AS id, r
                $$) AS (id agtype, element agtype);
            """)
            params = {
                "start_id": element.start_id,
                "end_id": element.end_id,
                "props": element.properties
            }
        else:  # 顶点类型
            query = text(f"""
                SELECT * FROM ag_catalog.cypher('my_graph', $$
                    CREATE (v:{element.label} {{name: 'Andres', title: 'Developer'}})
                $$) as (n ag_catalog.agtype);
            """)
            params = {"props": element.properties}
        
        result = await self.session.execute(
            query
        )
        row = result.one()
        element.id = json.loads(row.id)
        return element

    async def get(self, element_id: int) -> Optional[T]:
        """获取元素(顶点/边)"""
        query = text("""
            SELECT * FROM cypher(:graph_name, $$
                MATCH (e)
                WHERE id(e) = $element_id
                RETURN e
                UNION
                MATCH ()-[e]->()
                WHERE id(e) = $element_id
                RETURN e
            $$) AS (element agtype);
        """)
        result = await self.session.execute(
            query,
            {"graph_name": self.graph_name, "element_id": element_id}
        )
        if result.rowcount == 0:
            return None
        return json.loads(result.scalar())

    async def query(self, cypher: str, params: dict = None) -> List[Dict]:
        """执行Cypher查询"""
        result = await self.session.execute(
            text(f"SELECT * FROM cypher(:graph_name, $${cypher}$$) AS result"),
            {"graph_name": self.graph_name, **(params or {})}
        )
        return [json.loads(row[0]) for row in result]

    async def connect(self, 
                     from_id: int, 
                     to_id: int, 
                     rel_type: str, 
                     properties: dict = None) -> int:
        """创建关系"""
        query = text(f"""
            SELECT * FROM cypher(:graph_name, $$
                MATCH (a), (b)
                WHERE id(a) = $from_id AND id(b) = $to_id
                CREATE (a)-[r:{rel_type} $props]->(b)
                RETURN id(r)
            $$) AS (id agtype);
        """)
        result = await self.session.execute(
            query,
            {
                "graph_name": self.graph_name,
                "from_id": from_id,
                "to_id": to_id,
                "props": properties or {}
            }
        )
        return json.loads(result.scalar())

    async def traverse(self, 
                      start_id: int, 
                      depth: int = 1,
                      direction: str = "OUTGOING") -> Dict:
        """图遍历"""
        arrow = "->" if direction == "OUTGOING" else "<-" if direction == "INCOMING" else "-"
        
        query = text(f"""
            SELECT * FROM cypher(:graph_name, $$
                MATCH path = (start){arrow}[*1..{depth}](end)
                WHERE id(start) = $start_id
                RETURN nodes(path) AS nodes, relationships(path) AS edges
            $$) AS (nodes agtype, edges agtype);
        """)
        
        result = await self.session.execute(
            query,
            {"graph_name": self.graph_name, "start_id": start_id}
        )
        
        row = result.one()
        return {
            "nodes": [json.loads(node) for node in json.loads(row.nodes)],
            "edges": [json.loads(edge) for edge in json.loads(row.edges)]
        }
    # 图管理功能
    async def create_graph(self) -> bool:
        """创建新图"""
        await self.session.execute(
            text("SELECT ag_catalog.create_graph(:graph_name)"),
            {"graph_name": self.graph_name}
        )
        await self.session.commit()
        return True

    async def drop_graph(self, cascade: bool = False) -> bool:
        """删除当前图"""
        query = "SELECT ag_catalog.drop_graph(:graph_name, :cascade)"
        await self.session.execute(
            text(query),
            {"graph_name": self.graph_name, "cascade": cascade}
        )
        await self.session.commit()
        return True

    async def graph_exists(self) -> bool:
        """检查当前图是否存在"""
        result = await self.session.execute(
            text("SELECT 1 FROM ag_catalog.ag_graph WHERE name = :graph_name"),
            {"graph_name": self.graph_name}
        )
        return result.scalar() is not None

    # 标签管理
    async def create_vertex_label(
        self,
        label_name: str,
        properties: Optional[Dict[str, str]] = None
    ) -> bool:
        """创建顶点标签"""
        await self.session.execute(
            text("SELECT * FROM ag_catalog.create_vlabel(:graph_name, :label_name)"),
            {"graph_name": self.graph_name, "label_name": label_name}
        )
        
        if properties:
            for prop_name, prop_type in properties.items():
                await self.add_vertex_property(label_name, prop_name, prop_type)
        
        await self.session.commit()
        return True

    async def add_vertex_property(
        self,
        label_name: str,
        property_name: str,
        property_type: str = "string"
    ) -> bool:
        """添加顶点属性"""
        type_mapping = {
            "string": "text",
            "int": "integer",
            "float": "float8",
            "bool": "boolean",
            "json": "jsonb"
        }
        
        query = text("""
            SELECT * FROM ag_catalog.alter_vlabel(
                :graph_name,
                :label_name,
                'ADD',
                :property_name,
                :property_type
            )
        """)
        await self.session.execute(
            query,
            {
                "graph_name": self.graph_name,
                "label_name": label_name,
                "property_name": property_name,
                "property_type": type_mapping.get(property_type, "text")
            }
        )
        return True

    async def create_edge_label(
        self,
        label_name: str,
        properties: Optional[Dict[str, str]] = None
    ) -> bool:
        """创建边标签"""
        await self.session.execute(
            text("SELECT * FROM ag_catalog.create_elabel(:graph_name, :label_name)"),
            {"graph_name": self.graph_name, "label_name": label_name}
        )
        
        if properties:
            for prop_name, prop_type in properties.items():
                await self.add_edge_property(label_name, prop_name, prop_type)
        
        await self.session.commit()
        return True

    async def add_edge_property(
        self,
        label_name: str,
        property_name: str,
        property_type: str = "string"
    ) -> bool:
        """添加边属性"""
        type_mapping = {
            "string": "text",
            "int": "integer",
            "float": "float8",
            "bool": "boolean",
            "json": "jsonb"
        }
        
        query = text("""
            SELECT * FROM ag_catalog.alter_elabel(
                :graph_name,
                :label_name,
                'ADD',
                :property_name,
                :property_type
            )
        """)
        await self.session.execute(
            query,
            {
                "graph_name": self.graph_name,
                "label_name": label_name,
                "property_name": property_name,
                "property_type": type_mapping.get(property_type, "text")
            }
        )
        return True

    # 索引管理
    async def create_vertex_index(
        self,
        label_name: str,
        property_name: Union[str, List[str]],
        index_type: str = "btree"
    ) -> bool:
        """创建顶点索引"""
        if isinstance(property_name, list):
            properties = ", ".join(property_name)
            query = f"""
                CREATE INDEX ON cypher(:graph_name, $$
                    MATCH (n:{label_name}) 
                    RETURN {properties}
                $$) USING {index_type}
            """
        else:
            query = f"""
                CREATE INDEX ON cypher(:graph_name, $$
                    MATCH (n:{label_name}) 
                    RETURN n.{property_name}
                $$) USING {index_type}
            """
        
        await self.session.execute(
            text(query),
            {"graph_name": self.graph_name}
        )
        await self.session.commit()
        return True

    async def create_edge_index(
        self,
        label_name: str,
        property_name: Union[str, List[str]],
        index_type: str = "btree"
    ) -> bool:
        """创建边索引"""
        if isinstance(property_name, list):
            properties = ", ".join(property_name)
            query = f"""
                CREATE INDEX ON cypher(:graph_name, $$
                    MATCH ()-[r:{label_name}]->() 
                    RETURN {properties}
                $$) USING {index_type}
            """
        else:
            query = f"""
                CREATE INDEX ON cypher(:graph_name, $$
                    MATCH ()-[r:{label_name}]->() 
                    RETURN r.{property_name}
                $$) USING {index_type}
            """
        
        await self.session.execute(
            text(query),
            {"graph_name": self.graph_name}
        )
        await self.session.commit()
        return True
    
    
if __name__ == "__main__":
    from common.utils.dataBase.DataBasePostgre import DataBasePostgre
    from config.index import conf
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
            database_config["database"]
        )
        database_sqlite_default.connect()
        engine = database_sqlite_default.engine
        session = database_sqlite_default.sessionFactory()
        orm = GraphPostgre(session)
        
        try:
            # 检查图是否存在，不存在则创建
            if not await orm.graph_exists():
                await orm.create_graph()
                print(f"Created graph '{orm.graph_name}'")
            
            # # 创建顶点标签和属性
            # await orm.create_vertex_label("Person", {
            #     "name": "string",
            #     "age": "int"
            # })
            
            # # 创建边标签和属性
            # await orm.create_edge_label("KNOWS", {
            #     "since": "int"
            # })
            
            # 创建顶点
            alice = Person(properties={"name": "Alice", "age": 30})
            alice = await orm.create(alice)
            print(f"Created Alice with ID: {alice.id}")
            
            bob = Person(properties={"name": "Bob", "age": 35})
            bob = await orm.create(bob)
            print(f"Created Bob with ID: {bob.id}")
            
            # 创建边
            knows = Knows(start_id=alice.id, end_id=bob.id, properties={"since": 2020})
            await orm.create(knows)
            print("Created KNOWS relationship between Alice and Bob")
            
            # 图遍历查询
            print("\nTraversing from Alice:")
            result = await orm.traverse(alice.id, depth=2)
            for node in result["nodes"]:
                print(f"Node: {node}")
            for edge in result["edges"]:
                print(f"Edge: {edge}")
            
            # 原始Cypher查询
            print("\nQuerying people over age 25:")
            data = await orm.query("""
                MATCH (p:Person) 
                WHERE p.age > $min_age 
                RETURN p
            """, {"min_age": 25})
            
            for person in data:
                print(f"Found: {person}")
                
        finally:
            await session.close()
            await engine.dispose()

    # 运行异步主函数
    import asyncio
    asyncio.run(main())