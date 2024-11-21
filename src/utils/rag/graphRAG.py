import asyncio
import sys
from pathlib import Path


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

    async def get_db():
        db = DataBaseNeo4j("neo4j", "111111", "localhost", "7687")
        await db.connect()
        await db.cypher_query("MATCH (n) DETACH DELETE n")
        return db

    async def main():
        # db = await get_db()
        project = r"D:\test\fastapi"
        project_name = "fastapi"
        # file_list,size = DirectoryTree.build_directory_list(project)
        file_list,size = DirectoryTree.build_directory_list(project)
        print(json.dumps(file_list, ensure_ascii=False, indent=4),size)
        
        
        # for file in file_list:
        #     await db.cypher_query(
        #         f"""
        #             CREATE (f:File {{ 
        #                 project:'{project_name}',
        #                 name: $label, 
        #                 path: $path, 
        #                 size: $size
        #                 }})
        #         """,
        #         file,
        #     )
        #     print(f'处理完成{file["path"]}...')


        # path_grapg_db ="D:/test/kuzu_db"
        #  user: str, pwd: str, host: str, port

        # file = {"name": "test.py", "vector": "todo", "size": "todo", "doc": "todo"}
        # await db.cypher_query(
        #     """
        #     CREATE (f:File {
        #         name: $name,
        #         vector: $vector,
        #         size: $size,
        #         doc: $doc })
        #     """,
        #     file,
        # )
        # directory_tree

    # 运行主函数
    asyncio.run(main())
