import sys
from pathlib import Path

# 获取当前文件的绝对路径，然后向上移动两级目录
parent_path = Path(__file__).resolve().parent.parent.parent
# 将目标目录添加到系统路径中
sys.path.append(str(parent_path))
print(sys.path)
import json


if __name__ == "__main__":

    # 文件遍历
    from utils.file.directory_tree import DirectoryTree
    from graphRAG.graph import Graph

    # directory_tree = DirectoryTree.build_directory_tree(r'D:\test\fastapi')
    # # 将目录树转换为 JSON 格式
    # json_tree = json.dumps(
    #     directory_tree,
    #     #默认输出ASCLL码，False可以输出中文。
    #     # 带格式
    #     indent=4,
    #     ensure_ascii=False,
    # )
    # print(json_tree)
    
    path_grapg_db ="D:/test/kuzu_db"
    graph = Graph(path_grapg_db)
    # graph.refresh(path_grapg_db)
    graph.create()
