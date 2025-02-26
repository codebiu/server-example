import sys, pathlib
[sys.path.append(str(pathlib.Path(__file__).resolve().parents[i])) for i in range(4)]
from common.utils.code.tree_sitter_codes import TreeSitterlanguages
import pytest
from enum import Enum, auto
from tree_sitter import Tree, Parser
from src.common.utils.enum.code import CodeType





if __name__ == "__main__":
    import time
    tree_sitter = TreeSitterlanguages("temp","temp")
    # tree_sitter.build([CodeType.java])   
    # tree_sitter.build([CodeType.python])   
    # tree_sitter.build([CodeType.dart])   
    tree_sitter.build([CodeType.javascript])   

    # 读取python文件到字符串
    # with open(r"D:\test\fastapi\routing.py", "r", encoding="utf-8") as f:
    with open(r"test-data\text\test.java", "r", encoding="utf-8") as f:
        text_str = f.read()
        start_time = time.time()
        new_chunks = tree_sitter.code2tree(CodeType.java,text_str)
        print(new_chunks.root_node)
        print(time.time() - start_time)
        
    with open(r"test-data\text\test.dart", "r", encoding="utf-8") as f:
        text_str = f.read()
        start_time = time.time()
        new_chunks = tree_sitter.code2tree(CodeType.dart,text_str)
        print(new_chunks.root_node)
        print(time.time() - start_time)
    with open(r"test-data\text\test.py", "r", encoding="utf-8") as f:
        text_str = f.read()
        start_time = time.time()
        new_chunks = tree_sitter.code2tree(CodeType.python,text_str)
        print(new_chunks.root_node)
        print(time.time() - start_time)
    with open(r"test-data\text\test.js", "r", encoding="utf-8") as f:
        text_str = f.read()
        start_time = time.time()
        new_chunks = tree_sitter.code2tree(CodeType.javascript,text_str)
        print(new_chunks.root_node)
        print(time.time() - start_time)