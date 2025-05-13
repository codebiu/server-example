from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select,text
# self
from config.db import Data, DataNoCommit


class AgeDao:
    def __init__(self, session: AsyncSession):
        self.session = session

    def create_graph(self, graph_name: str):
        self.session.execute(text(f"SELECT * FROM ag_catalog.create_graph('{graph_name}');"))
        self.session.commit()
    
    def cypher_query(self, graph_name: str, query: str, params: dict = None):
        """执行 Cypher 查询"""
        sql = f"SELECT * FROM cypher('{graph_name}', $${query}$$) as (result agtype);"
        return self.session.execute(text(sql), params or {}).fetchall()
    
    def add_vertex(self, graph_name: str, label: str, properties: dict):
        """添加顶点"""
        props_str = ", ".join(f"{k}: ${k}" for k in properties.keys())
        query = f"CREATE (:{label} {{{props_str}}}) RETURN id;"
        return self.cypher_query(graph_name, query, properties)
    
    def add_edge(self, graph_name: str, start_id: int, end_id: int, rel_type: str, properties: dict = None):
        """添加边关系"""
        props = properties or {}
        query = f"""
        MATCH (a), (b)
        WHERE id(a) = $start_id AND id(b) = $end_id
        CREATE (a)-[r:{rel_type} $props]->(b)
        RETURN r;
        """
        params = {"start_id": start_id, "end_id": end_id, "props": props}
        return self.cypher_query(graph_name, query, params)
