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


if __name__ == "__main__":
    from utils.dataBase.DataBaseNeo4j import DataBaseNeo4j

    # 文件遍历
    from utils.file.directory_tree import DirectoryTree

    # from utils.rag.graphRAG.KuzuGraph import KuzuGraph
    import polars as pl

    # def get_file_info(file_path):
    #     directory_list = DirectoryTree.build_directory_list(file_path)
    #     # 将目录树转换为 JSON 格式
    #     json_list  = json.dumps( directory_list, ensure_ascii=False)
    #     return json_list

    def get_db():
        db = DataBaseNeo4j("neo4j", "1111111", "localhost", "7687")
        db.connect()
        db.cypher_query("MATCH (n) DETACH DELETE n")
        return db

    async def main():
        start_time = time.time()
        db = get_db()
        print("db连接", time.time() - start_time)
        start_time = time.time()
        project = r"D:\test\fastapi"
        project_name = "fastapi"
        # file_list,size = DirectoryTree.build_directory_list(project)
        directory_list = DirectoryTree.build_directory_list_root(project)
        # print(json.dumps(file_list, ensure_ascii=False, indent=4),size)
        # file_list 中type为'file'的节点
        file_list = [file for file in directory_list if file["type"] == "File"]
        folder_list = [file for file in directory_list if file["type"] == "Folder"]
        print("解析文件树：", time.time() - start_time)
        start_time = time.time()
        query_create_file = f"""
                    CREATE (f:File {{ 
                        name: $label, 
                        path: $path, 
                        size: $size
                        }})
                    """
        query_create_folder = f"""
                    CREATE (f:Folder {{ 
                        name: $label, 
                        path: $path, 
                        size: $size
                        }})
                    """
        start_time = time.time()
        db.cypher_query_batchs(
            [
                {"query": query_create_file, "params": file_list},
                {"query": query_create_folder, "params": folder_list},
            ]
        )
        print("创建文件节点：", time.time() - start_time)
        start_time = time.time()
        # 关联文件文件夹 file 路径[0,1]去除最后一个[0]和1与文件夹路径[0]name1的1对齐
        relation_folder_file = f"""MATCH (f:File), (d:Folder) 
                                    WHERE f.path[..-1] = d.path AND f.path[-1] = d.name
                                    MERGE (d)-[:include]->(f)
                                """
        # 关联文件夹 防止文件夹文件同名 单独处理文件夹从属关系
        relation_folder_folder = f"""MATCH (f:Folder), (d:Folder) 
                                    WHERE f.path[..-1] = d.path AND f.path[-1] = d.name
                                    MERGE (d)-[:include]->(f)
                                """
        db.cypher_query_batchs(
            [{"query": relation_folder_file}, {"query": relation_folder_folder}]
        )
        print("创建关系：", time.time() - start_time)
        
        # 解析文件语法树
        
        
    # 运行主函数
    asyncio.run(main())
