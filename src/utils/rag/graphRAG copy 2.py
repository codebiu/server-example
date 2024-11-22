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
        db = DataBaseNeo4j("neo4j", "here111111", "localhost", "7687")
        db.connect()
        db.cypher_query("MATCH (n) DETACH DELETE n")
        return db

    async def main():
        db = get_db()
        project = r"D:\test\fastapi"
        project_name = "fastapi"
        # file_list,size = DirectoryTree.build_directory_list(project)
        directory_list, size = DirectoryTree.build_directory_list(project)
        # print(json.dumps(file_list, ensure_ascii=False, indent=4),size)
        # file_list 中type为'file'的节点
        file_list = [file for file in directory_list if file["type"] == "File"]
        folder_list = [file for file in directory_list if file["type"] == "Folder"]

        query_create_project = f"""
            CREATE (f:Project {{ 
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
        query_create_file = f"""
                    CREATE (f:File {{ 
                        name: $label, 
                        path: $path, 
                        size: $size
                        }})
                    """

        start_time = time.time()
        query_objs = [
            {
                "query": query_create_project,
                "params": [{"label": project_name, "path": project_name, "size": size}],
            },
            {"query": query_create_folder, "params": folder_list},
            {"query": query_create_file, "params": file_list},
        ]
        for query_obj in query_objs:
            params_list = query_obj["params"]
            query = query_obj["query"]
            db.cypher_query_batch(query, params_list)
        print("创建文件节点时间：", time.time() - start_time)

    # 运行主函数
    asyncio.run(main())
