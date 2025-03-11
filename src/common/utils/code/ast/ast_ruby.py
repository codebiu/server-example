from tree_sitter import Node
from utils.multi_ast.ast import Ast
from utils.enum_code import CodeType
from utils.tree_sitter_codes import TreeSitterCodes
import uuid

tree_sitter_options = {
    "query": """
                ;; import
                (call 
                    method: (identifier) @_import
                        (#match? @_import "^(require|require_relative)$") 
                )@import
                (call 
                    method: (identifier) @_import
                    arguments: 
                        (argument_list 
                            (string 
                                (string_content) @name
                            )
                        )
                        (#match? @_import "^(require|require_relative)$") 
                )
                ;; 类外entity
                (program
                    (assignment
                        left: [
                            (identifier) @name
                            (instance_variable) @name
                            (class_variable) @name
                        ]
                    ) @entity
                )
                ;; 类外多entity
                (program
                    (assignment
                        left:(left_assignment_list
                         (_)
                        ) 
                    )? @entity
                )
                (program
                    (assignment
                        left:(left_assignment_list
                        (_)@name
                        ) 
                    )
                )
                ;; 类外函数
                (program
                    (method 
                    ;;todo identifier|
                        name: (_) @name 
                    )? @function
                )
                ;; 类
                (program
                    (class 
                        name:  (constant) @name 
                    )@class
                )
                ;; 类内entity
                (program
                    (class 
                        name:  (constant)
                        body: 
                            (body_statement 
                                 (assignment
                                    left: [
                                        (identifier) @name
                                        (instance_variable) @name
                                        (class_variable) @name
                                    ]
                                ) @entity
                            )
                    )
                )
                (program
                    (class 
                        name:  (constant)
                        body: 
                            (body_statement 
                                 (assignment
                                    left:(left_assignment_list
                                    (_)
                                    ) 
                                )? @entity
                            )
                    )
                )
                (program
                    (class 
                        name:  (constant)
                        body: 
                            (body_statement 
                                 (assignment
                                    left:(left_assignment_list
                                            (_)@name
                                        )
                                ) 
                            )
                    )
                )
                ;; 类内函数
                (program
                    (class 
                        name:  (constant)
                        body: 
                            (body_statement 
                                (_  
                                    name: (_) @name 
                                )? @function
                            )
                    )
                )
                ;; module
                (program
                    (module 
                        name:  (constant) @name 
                    )@class
                )
                ;; module内entity
                (program
                    (module 
                        name:  (constant)
                        body: 
                            (body_statement 
                                 (assignment
                                    left: [
                                        (identifier) @name
                                        (instance_variable) @name
                                        (class_variable) @name
                                    ]
                                ) @entity
                            )
                    )
                )
                (program
                    (module 
                        name:  (constant)
                        body: 
                            (body_statement 
                                 (assignment
                                    left:(left_assignment_list
                                    (_)
                                    ) 
                                )? @entity
                            )
                    )
                )
                (program
                    (module 
                        name:  (constant)
                        body: 
                            (body_statement 
                                 (assignment
                                    left:(left_assignment_list
                                            (_)@name
                                        )
                                ) 
                            )
                    )
                )
                ;; module内函数
                (program
                    (module 
                        name:  (constant)
                        body: 
                            (body_statement 
                                (_  
                                    name: (_) @name 
                                )? @function
                            )
                    )
                )
                ;; 特殊节点
                ;; 特殊类  
                (program
                    (class 
                        name: 
                            (scope_resolution
                                name:(constant)@name 
                            ) 
                    )@class
                )
                  ;; 类
                ;; 类内entity
                (program
                    (class 
                        name: (scope_resolution
                                name:(constant)
                            ) 
                        body: 
                            (body_statement 
                                 (assignment
                                    left: [
                                        (identifier) @name
                                        (instance_variable) @name
                                        (class_variable) @name
                                    ]
                                ) @entity
                            )
                    )
                )
                (program
                    (class 
                        name: (scope_resolution
                                name:(constant)
                            ) 
                        body: 
                            (body_statement 
                                 (assignment
                                    left:(left_assignment_list
                                    (_)
                                    ) 
                                )? @entity
                            )
                    )
                )
                (program
                    (class 
                        name:  (scope_resolution
                                name:(constant)
                            ) 
                        body: 
                            (body_statement 
                                 (assignment
                                    left:(left_assignment_list
                                            (_)@name
                                        )
                                ) 
                            )
                    )
                )
                ;;;;函数
                (program
                    (class 
                        name:  (scope_resolution
                                name:(constant)
                            ) 
                        body: 
                            (body_statement 
                                (_  
                                    name: (_) @name 
                                )? @function
                            )
                    )
                )
                """
}

class AstRuby(Ast):
    """ast分析代码"""
    def __init__(self):
        tree_sitter_languages = TreeSitterCodes("tree-sitter", "tree-sitter/source")
        self.parser = tree_sitter_languages.get_parser(CodeType.ruby)
        self.language = tree_sitter_languages.get_language(CodeType.ruby)
        self.tree_sitter_options = tree_sitter_options
        self.query = self.language.query(tree_sitter_options["query"])
    def _captures_deal(self,captures,text_bytes):
        """过滤修改节点"""
        new_captures = []
        i = 0  # 初始化计数器\
        # 遍历有效代码块code_block
        captures_len = len(captures)
        while i < captures_len:
            capture = captures[i]
            # code_block_node: Node = capture[0]
            code_block_name: str = capture[1]
            # 过滤无关节点
            if not code_block_name.startswith("_"):
                new_captures.append(capture)
            i+= 1
        del captures
        return new_captures

if __name__ == "__main__":
    import time

    # 创建分割器
    chunker = AstRuby()
    start_time = time.time()

    # 读取python文件到字符串
    with open(r"test-data\text\main.rb", "r", encoding="utf-8") as f:
        text_bytes = f.read()
        print(time.time() - start_time)
        start_time = time.time()
        new_chunks = chunker.chunk(text_bytes)
        # print(new_chunks)
        print(time.time() - start_time)
        start_time = time.time()
