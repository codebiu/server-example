from tree_sitter import Node
from utils.multi_ast.ast import Ast
from utils.enum_code import CodeType
from utils.tree_sitter_codes import TreeSitterCodes
import uuid

tree_sitter_options = {
    "query": """
                ;; import
                (program
                    (import_declaration) @import
                )
                (program
                    (import_declaration
                        (scoped_identifier)@name
                    )
                )
                ;; 类
                (program
                    (class_declaration 
                        name:  (identifier) @name 
                    )@class
                )
                ;; 类内entity(单/多)
                (program
                    (class_declaration 
                        name:  (identifier)
                        body: 
                            (class_body 
                                 (field_declaration) @entity
                            )
                    )
                )
                ;; 类内多entity
                (program
                    (class_declaration 
                        name:  (identifier)
                        body: 
                            (class_body 
                                 (field_declaration
                                    declarator: 
                                                (variable_declarator
                                                    name: (identifier) @name
                                                )
                                 ) 
                            )
                    )
                )
                ;; 类内 function
                (program
                    (class_declaration 
                        name:  (identifier)
                        body: 
                            (class_body 
                                 (method_declaration
                                    name: (identifier) @name
                                 )@function
                            )
                    )
                )
            """
}

class AstJava(Ast):
    """ast分析代码"""
    def __init__(self):
        tree_sitter_languages = TreeSitterCodes("tree-sitter", "tree-sitter/source")
        self.parser = tree_sitter_languages.get_parser(CodeType.java)
        self.language = tree_sitter_languages.get_language(CodeType.java)
        self.tree_sitter_options = tree_sitter_options
        self.query = self.language.query(tree_sitter_options["query"])

if __name__ == "__main__":
    import time

    # 创建分割器
    chunker = AstJava()
    start_time = time.time()

    # 读取python文件到字符串
    with open(r"test-data\text\test.java", "r", encoding="utf-8") as f:
        text_bytes = f.read()
        print(time.time() - start_time)
        start_time = time.time()
        new_chunks = chunker.chunk(text_bytes)
        # print(new_chunks)
        print(time.time() - start_time)
        start_time = time.time()
