# lib
import asyncio
import sys
from pathlib import Path
import time

# 获取当前文件的绝对路径，然后向上移动两级目录
parent_path = Path(__file__).resolve().parent.parent.parent
# 将目标目录添加到系统路径中
sys.path.append(str(parent_path))
print(sys.path)
import json

# self

from utils.ast.ast_python import AstPython

# 文件遍历
from utils.file.directory_tree import DirectoryTree


class GraphRAG:
    def __init__(self, project_path, project_name):
        self.project = project_path
        self.project_name = project_name
        self.chunker = AstPython()

    def _get_db(self, db):
        self.db = db
        self.db.connect()

    def _clear(self):
        self.db.cypher_query("MATCH (n) DETACH DELETE n")

    def _file_tree(self):
        self.directory_tree = DirectoryTree.build_directory_tree_root(self.project)

    def _graph_file(self):
        # 考虑文件迁移问题?
        start_time = time.time()
        self.cypterObj = {
            "query_create_file": f"""
                    CREATE (f:File {{ 
                        name: $label, 
                        path: $path, 
                        size: $size
                        }})
                    """,
            "query_create_folder": f"""
                                CREATE (f:Folder {{ 
                                    name: $label, 
                                    path: $path, 
                                    size: $size
                                    }})
                                """,
            "relation_folder_folder": f"""
                    MERGE (p:Folder {{name: $plabel, path: $ppath, size: $psize}})
                    MERGE (s:Folder {{name: $label, path: $path, size: $size}})
                    CREATE (s)-[:in]->(p)
                    """,
            "relation_folder_file": f"""
                    MERGE (p:Folder {{name: $plabel, path: $ppath, size: $psize}})
                    CREATE (s:File {{name: $label, path: $path, size: $size}})
                    CREATE (s)-[:in]->(p)
                    """,
            "relation_file_class": f"""
                    MERGE (p:File {{name: $label, path: $path, size: $size}})
                    CREATE (s:Class {{name: $name, byte_range: $byte_range, argument_list: $argument_list}})
                    CREATE (s)-[:belong]->(p)
            """,
            "relation_class_function": f"""
                    MERGE (p:Class {{name: $node_class.name, byte_range: $node_class.byte_range, argument_list: $node_class.argument_list}})
                    CREATE (s:Function {{name: $node_function.name, byte_range: $node_function.byte_range, argument_list: $node_function.argument_list}})
                    CREATE (s)-[:belong]->(p)
            """,
            # "relation_file_function": f"""
            #         MERGE (p:Class {{name: $label, path: $path, size: $size}})
            #         CREATE (s:Class {{name: $name, byte_range: $byte_range, argument_list: $argument_list}})
            #         CREATE (s)-[:belong]->(p)
            # """,
            # "insert_call_file": f"""
            #         MERGE (p:File {{name: $label, path: $path, size: $size}})
            #         CREATE (s:Class {{name: $name, byte_range: $byte_range, argument_list: $argument_list}})
            #         CREATE (s)-[:belong]->(p)
            # """,
        }
        self._graph_tree_all(self.directory_tree)
        print("创建关系：", time.time() - start_time)

    def _graph_tree_all(self, node: dict, parent_node=None):
        """迭代创建节点插入图"""
        if "children" in node:
            # Folder
            self.db.cypher_query(self.cypterObj["query_create_folder"], node)
            # 关联父子文件夹
            if parent_node is not None:
                self.db.cypher_query(
                    self.cypterObj["relation_folder_folder"],
                    {
                        "plabel": parent_node["label"],
                        "ppath": parent_node["path"],
                        "psize": parent_node["size"],
                        "label": node["label"],
                        "path": node["path"],
                        "size": node["size"],
                    },
                )
            for child in node["children"]:
                self._graph_tree_all(child, node)
        else:
            # 文件处理
            self.db.cypher_query(
                self.cypterObj["relation_folder_file"],
                {
                    "plabel": parent_node["label"],
                    "ppath": parent_node["path"],
                    "psize": parent_node["size"],
                    "label": node["label"],
                    "path": node["path"],
                    "size": node["size"],
                },
            )
            
            {
  "功能": "待填",
  "调用关系": [
      {"调用方方法":"待填"}
  ]
}
            # ast
            chunk = self.astCode_neo(node)
            if chunk is not None:
                for node_class in chunk["class"]:
                    self.db.cypher_query(
                        self.cypterObj["relation_file_class"],
                        node|node_class,
                    )
                    # class 子函数
                    for node_function in node_class['function']:
                        self.db.cypher_query(
                            self.cypterObj["relation_class_function"],
                            {
                                node_function:node_function,
                                node_class:node_class,
                            }
                        )
                    

    # def _file_tree(self):
    #      # file_list,size = DirectoryTree.build_directory_list(project)
    #     directory_list = DirectoryTree.build_directory_list_root(self.project)
    #     # print(json.dumps(file_list, ensure_ascii=False, indent=4),size)
    #     # file_list 中type为'file'的节点
    #     self.file_list = [file for file in directory_list if file["type"] == "File"]
    #     self.folder_list = [file for file in directory_list if file["type"] == "Folder"]

    # def _graph_file(self):
    #     # 考虑文件迁移问题?
    #     start_time = time.time()
    #     query_create_file = f"""
    #                 CREATE (f:File {{
    #                     name: $label,
    #                     path: $path,
    #                     size: $size
    #                     }})
    #                 """
    #     query_create_folder = f"""
    #                 CREATE (f:Folder {{
    #                     name: $label,
    #                     path: $path,
    #                     size: $size
    #                     }})
    #                 """
    #     start_time = time.time()
    #     self.db.cypher_query_batchs(
    #         [
    #             {"query": query_create_file, "params": self.file_list},
    #             {"query": query_create_folder, "params": self.folder_list},
    #         ]
    #     )
    #     print("创建文件节点：", time.time() - start_time)
    #     start_time = time.time()
    #     # 关联文件文件夹 file 路径[0,1]去除最后一个[0]和1与文件夹路径[0]name1的1对齐
    #     relation_folder_file = f"""MATCH (f:File), (d:Folder)
    #                                 WHERE f.path[..-1] = d.path AND f.path[-1] = d.name
    #                                 MERGE (d)-[:include]->(f)
    #                             """
    #     # 关联文件夹 防止文件夹文件同名 单独处理文件夹从属关系
    #     relation_folder_folder = f"""MATCH (f:Folder), (d:Folder)
    #                                 WHERE f.path[..-1] = d.path AND f.path[-1] = d.name
    #                                 MERGE (d)-[:include]->(f)
    #                             """
    #     self.db.cypher_query_batchs(
    #         [{"query": relation_folder_file}, {"query": relation_folder_folder}]
    #     )
    #     print("创建关系：", time.time() - start_time)

    # def astCode(self):
    #     start_time = time.time()
    #     new_chunks = []
    #     # self.file_list
    #     for file in self.file_list:
    #         file_path = file["path_full"]
    #         if file_path.endswith(".py"):
    #             # 读取python文件到字符串
    #             with open(file_path, "r", encoding="utf-8") as f:
    #                 text = f.read()
    #                 new_chunk = self.chunker.chunk(text)
    #                 new_chunks.append(new_chunk)
    #     print("astcode", time.time() - start_time)
    def astCode_neo(self, node_file):
        file_path = node_file["path"]
        if file_path.endswith(".py"):
            # 读取python文件到字符串
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
                new_chunk = self.chunker.chunk(text)
                return new_chunk

    def create(self, db):
        start_time = time.time()
        self._get_db(db)
        self._clear()
        print("重置数据库", time.time() - start_time)
        self._file_tree()
        self._graph_file()
        # self.astCode()


if __name__ == "__main__":
    from utils.dataBase.DataBaseNeo4j import DataBaseNeo4j

    # from utils.rag.graphRAG.KuzuGraph import KuzuGraph
    import polars as pl

    async def main():
        start_time = time.time()
        print("db连接", time.time() - start_time)
        start_time = time.time()
        project = r"D:\test\fastapi"
        project_name = "fastapi"
        db = DataBaseNeo4j("neo4j", "111111", "localhost", "7687")
        graphRAG = GraphRAG(project, project_name)
        graphRAG.create(db)

    # 运行主函数
    asyncio.run(main())
