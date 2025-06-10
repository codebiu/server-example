import time
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, SessionExpired
from common.utils.db.DataBaseInterface import DataBaseInterface


class DataBaseNeo4j(DataBaseInterface):
    def __init__(self, user: str, pwd: str, host: str, port: int, path: str = "neo4j"):
        self.url = f"neo4j://{host}:{port}"
        self.user = user
        self.pwd = pwd
        self.path = path  # 指定默认数据库
        self.driver = None

    def connect(self):
        """建立与 Neo4j 数据库的连接"""
        self.driver = GraphDatabase.driver(
            self.url,
            auth=(self.user, self.pwd),
            database=self.path,
            max_connection_pool_size=100,
        )

    def cypher_query(self, query: str, params: dict = None):
        """执行 Cypher 查询并返回结果"""
        with self.driver.session() as session:
            result = session.run(query, params)
            return result

    def match_query(self, query: str, params: dict = None):
        """执行 Cypher 查询并返回记录列表"""
        with self.driver.session() as session:
            result = session.run(query, params)
            records = [record.data() for record in result]
            return records

    def create_node(self, label: str, properties: dict):
        """创建一个带有标签和属性的节点"""
        props_str = ", ".join([f"{key}: ${key}" for key in properties.keys()])
        query = f"CREATE (n:{label} {{{props_str}}}) RETURN n"
        return self.cypher_query(query, properties)

    def create_relationship(
        self,
        start_node_label: str,
        start_node_id: str,
        end_node_label: str,
        end_node_id: str,
        rel_type: str,
        rel_properties: dict = None,
    ):
        """在两个节点之间建立关系"""
        rel_props_str = (
            ""
            if not rel_properties
            else ", " + ", ".join([f"{key}: ${key}" for key in rel_properties.keys()])
        )
        query = f"MATCH (a:{start_node_label} {{id: $startNodeId}}), (b:{end_node_label} {{id: $endNodeId}}) CREATE (a)-[r:{rel_type}{rel_props_str}]->(b) RETURN r"
        params = {
            "startNodeId": start_node_id,
            "endNodeId": end_node_id,
            **(rel_properties or {}),
        }
        return self.cypher_query(query, params)

    def run_in_transaction(self, function, *args, **kwargs):
        """在一个事务中运行给定的函数"""
        with self.driver.session() as session:
            try:
                with session.begin_transaction() as tx:
                    result = function(tx, *args, **kwargs)
                    return result
            except (ServiceUnavailable, SessionExpired) as e:
                print(f"Transaction failed due to {e}")
                return None

    def disconnect(self):
        """关闭与 Neo4j 数据库的连接"""
        if self.driver is not None:
            self.driver.close()
            self.driver = None





# 示例用法
if __name__ == "__main__":
    db = DataBaseNeo4j(user="neo4j", pwd="password", host="localhost", port=7687)
    db.connect()
    # 创建节点
    node1 = db.create_node("Person", {"id": "1", "name": "Alice", "age": 30})
    # 创建关系
    rel = db.create_relationship(
        "Person", "1", "Person", "2", "FRIENDS", {"since": 2010}
    )
    db.disconnect()
    
    # MATCH (n)-[]->(m) where id(m)=43 RETURN DISTINCT n
    
    # MATCH (n) where n.path = 'D:\\test\\fastapi' RETURN n
