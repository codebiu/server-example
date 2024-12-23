import json
from neo4j.graph import Node, Path, Relationship

class Neo4jEX:
    """neo4j查询结果转成前端需要的格式"""

    def __init__(self):
        self.nodes = set()
        self.categories = set()
        self.links = []

    def refresh(self):
        self.nodes = set()
        self.links = []

    def get_graph(self, query):
        # 执行 Cypher 查询
        results, meta = db.cypher_query(query)
        for record in results:
            # path = record[0]
            for path in record:
                # path区分Node和relationship
                if isinstance(path, Node):
                    node_this = Neo4jEX.format_node(path)
                    self.nodes.add(json.dumps(node_this))
                    self.categories.add(json.dumps(Neo4jEX.format_categories(node_this)))
                elif isinstance(path, Relationship):
                    self.links.append(json.dumps(Neo4jEX.format_relationship(path)))
                else:
                    # Path
                    # start_node
                    start_node = Neo4jEX.format_node(path.start_node)
                    self.nodes.add(json.dumps(start_node))
                    self.categories.add(json.dumps(Neo4jEX.format_categories(start_node)))
                    # end_node
                    end_node = Neo4jEX.format_node(path.end_node)
                    self.nodes.add(json.dumps(end_node))
                    self.categories.add(json.dumps(Neo4jEX.format_categories(end_node)))
                    # relationship
                    for relationship in path.relationships:
                        self.links.append(json.dumps(Neo4jEX.format_relationship(relationship)))
        # 格式化
        nodes_list_string = list(self.nodes)
        # 转为dict
        nodes_dict = [json.loads(node) for node in nodes_list_string]
        links_dict = [json.loads(edge) for edge in self.links]
        categories_dict = [json.loads(category) for category in self.categories]
        graph_full = {
            "categories": categories_dict,
            "nodes": nodes_dict,
            "links": links_dict,
        }
        return graph_full

    @staticmethod
    def format_node(path: Node):
        """节点格式化"""
        category_full = ""
        # path.categorys
        for category in path.labels:
            if category_full == "":
                category_full = category_full + category
            else:
                category_full = category_full + "," + category
        # 获取
        node_this = {
            "id": path.id,
            "category": category_full,
            "properties": path._properties,
        }

        return node_this

    @staticmethod
    def format_relationship(relationship: Relationship):
        """关系格式化"""
        relationship_this = {
            "id": relationship.id,
            "name": relationship.type,
            "source": relationship.start_node.id,
            "target": relationship.end_node.id,
        }
        return relationship_this

    @staticmethod
    def format_categories(node_this: Node):
        """获取节点类型"""
        # 获取
        categories_this = {
            "name": node_this["category"],
        }
        return categories_this
