from tree_sitter import Node
from utils.multi_ast.ast import Ast
from utils.enum_code import CodeType
from utils.tree_sitter_codes import TreeSitterCodes
import uuid

tree_sitter_options = {
    "query": """
             ;;类
             (program_definition
                 (identification_division
                    (".")
                    (".")
                    (program_name)@name
                )
             )@class
             
             ;;类内实体
             ;;方法
            """
}
# https://github.com/avishek-sen-gupta/cobol-rekt
"""
文件后缀:.cbl 、.cob 、.ccp 、.cpy 和 .sqb
 cobol文件: 包含一个或多个program_definition(结构和组成部分)
    program_definition包含以下4部分:
        IDENTIFICATION DIVISION(标识部):   PROGRAM-ID视为类名
        environment_division(环境部):      包含多个实体(文件io和环境变量)
        DATA DIVISION(数据部):             包含多个实体(变量常量文件标识)
        PROCEDURE DIVISION(过程部):        包含多个方法体(考虑main和私有函数)   可以没有方法名时默认成MAIN-LOGIC.
"""
class AstCobol(Ast):
    """ast分析代码"""
    def __init__(self):
        tree_sitter_languages = TreeSitterCodes("tree-sitter", "tree-sitter/source")
        self.parser = tree_sitter_languages.get_parser(CodeType.cobol)
        self.language = tree_sitter_languages.get_language(CodeType.cobol)
        self.tree_sitter_options = tree_sitter_options
        self.query = self.language.query(tree_sitter_options["query"])

    def _captures_deal(self, captures, text_bytes):
        """处理COBOL特定的节点捕获
        将program_definition视为class
        将procedure_division下的paragraph视为method
        """
        processed_captures = []
        i = 0
        while i < len(captures):
            node, tag = captures[i]
            
            if tag == "class":
                # 查找关联的name节点
                name_node = None
                for j in range(i + 1, len(captures)):
                    if captures[j][1] == "name":
                        name_node = captures[j][0]
                        i = j  # 跳过已处理的name节点
                        break
                
                if name_node:
                    processed_captures.append([node, "class"])
                    processed_captures.append([name_node, "name"])
            
            # 处理方法节点
            elif tag == "method":
                processed_captures.append([node, "method"])
                # 查找方法名
                for j in range(i + 1, len(captures)):
                    if captures[j][1] == "name":
                        processed_captures.append([captures[j][0], "name"])
                        i = j
                        break
            i += 1
        
        return processed_captures

if __name__ == "__main__":
    import time

    # 创建分割器
    chunker = AstCobol()
    start_time = time.time()

    # 读取python文件到字符串
    with open(r"test-data\text\test.cbl", "r", encoding="utf-8") as f:
        text_bytes = f.read()
        print(time.time() - start_time)
        start_time = time.time()
        new_chunks = chunker.chunk(text_bytes)
        # print(new_chunks)
        print(time.time() - start_time)
        start_time = time.time()
