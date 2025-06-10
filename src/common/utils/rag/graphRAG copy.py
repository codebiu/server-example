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
    from common.utils.db.DataBaseNeo4j import DataBaseNeo4jAsync

    # 文件遍历
    from common.utils.file.directory_tree import DirectoryTree

    # from common.utils.rag.graphRAG.KuzuGraph import KuzuGraph
    import polars as pl

    # def get_file_info(file_path):
    #     directory_list = DirectoryTree.build_directory_list(file_path)
    #     # 将目录树转换为 JSON 格式
    #     json_list  = json.dumps( directory_list, ensure_ascii=False)
    #     return json_list

    async def get_db():
        db = DataBaseNeo4jAsync("neo4j", "here111111", "localhost", "7687")
        await db.connect()
        await db.cypher_query("MATCH (n) DETACH DELETE n")
        return db

    async def main():
        db = await get_db()
        project = r"D:\test\fastapi"
        project_name = "fastapi"
        # file_list,size = DirectoryTree.build_directory_list(project)
        file_list,size = DirectoryTree.build_directory_list(project)
        
        
        async def taskFuc(file, session):
            print(f'Task {file["path"]} started at {time.strftime("%X")}')
            await session.run(
                f"""
                    CREATE (f:File {{ 
                        project:'{project_name}',
                        name: $label, 
                        path: $path, 
                        size: $size
                        }})
                """,
                file,
            )
            print(f'Task {file["path"]} finished at {time.strftime("%X")}')

  
        start_time = time.time()
        async with db.sessionFactory() as session:
            tasks = []
            for file in file_list:
                tasks.append(taskFuc(file, session))
            await asyncio.gather(*tasks)
        print(f"All tasks completed in {time.time() - start_time:.2f} seconds")


    # 运行主函数
    asyncio.run(main())
