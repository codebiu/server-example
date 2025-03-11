from tree_sitter import Node
from utils.multi_ast.ast import Ast
from utils.enum_code import CodeType
from utils.tree_sitter_codes import TreeSitterCodes
import uuid

tree_sitter_options = {
    "query": """
                ;; import
                (program
                    (import_or_export
                       
                    ) @import
                )
                (program
                    (import_or_export
                        (library_import
                            (import_specification
                             (configurable_uri
                                (uri
                                    (string_literal)@name
                                )
                             )
                            )
                        )
                    )
                )
                ;; 类外entity  'static_final_declaration_list' 'initialized_identifier_list'
                (program
                    [
                        (const_builtin)
                        (final_builtin)
                        (inferred_type)
                        (type_identifier)
                    ]@entity_start
                    (_)
                    (";")
                )
                (program
                    [
                        (const_builtin)
                        (final_builtin)
                        (inferred_type)
                        (type_identifier)
                    ]
                    (_
                        (_
                            (identifier)@name
                        )
                    )
                    (";")
                )
                ; 结束和开始一致无效  语法树bug
                (program
                    [
                        (const_builtin)
                        (final_builtin)
                        (inferred_type)
                        (type_identifier)
                    ]
                    (_)
                    (";")@entity_end
                )

                ;; 类外函数
                (program
                   [
                        (function_signature
                            name:(identifier)@name
                        )
                        (getter_signature
                            name:(identifier)@name
                        )
                        (setter_signature
                            name:(identifier)@name
                        )
                    ]@function_start
                    (function_body)
                )
                (program
                    (function_body)@function_end
                )
                   
                ;;类
                (program
                    (class_definition
                       name: (identifier)@name
                    ) @class
                )
                ;; 类内实体
                (program
                    (class_definition
                       (class_body
                            (declaration
                                [
                                    (const_builtin)
                                    (final_builtin)
                                    (inferred_type)
                                    (type_identifier)
                                ]
                                (_
                                    (_
                                        (identifier)@name
                                    )
                                )
                            )@entity_start
                            (";")
                       )
                    )
                )
                (program
                    (class_definition
                       (class_body
                            (declaration
                                [
                                    (const_builtin)
                                    (final_builtin)
                                    (inferred_type)
                                    (type_identifier)
                                ]
                                (_)
                            )
                            (";")@entity_end
                       )
                    )
                )
            
                ;; 类内函数
                (program
                    (class_definition
                       (class_body
                            (method_signature
                                [
                                    (function_signature
                                        name:(identifier)@name
                                    )
                                    (getter_signature
                                        name:(identifier)@name
                                    )
                                    (setter_signature
                                        name:(identifier)@name
                                    )
                                    (factory_constructor_signature
                                        ("factory" .(identifier)@name)
                                    )
                                    (factory_constructor_signature
                                        ("factory")
                                        (identifier)@name
                                        (".")
                                        (identifier)@name
                                    )
                                ]@function_start
                            )
                            (function_body)
                       )
                    )
                )
                (program
                    (class_definition
                       (class_body
                            (method_signature)
                            (function_body)@function_end
                       )
                    )
                )
            
                """
}


class NodeSelf:
    def __init__(self):
        self.id: int = None
        self.start_byte: int = None
        self.end_byte: int = None
        self.start_point: tuple = None
        self.end_point: tuple = None
        self.type: str = None
        self.parent: Node = None


class AstDart(Ast):
    """ast分析代码"""

    def __init__(self):
        tree_sitter_languages = TreeSitterCodes("tree-sitter", "tree-sitter/source")
        self.parser = tree_sitter_languages.get_parser(CodeType.dart)
        self.language = tree_sitter_languages.get_language(CodeType.dart)
        self.tree_sitter_options = tree_sitter_options
        self.query = self.language.query(tree_sitter_options["query"])

    def _captures_deal(self, captures, text_bytes):
        """过滤修改节点"""
        new_captures = []
        to_del_set = set()
        i = 0  # 初始化计数器\
        # 遍历有效代码块code_block
        captures_len = len(captures)
        while i < captures_len:
            capture = captures[i]
            code_block_node: Node = capture[0]
            code_block_name: str = capture[1]
            next_index = i + 1
            # 起始分析节点->中间->结束节点
            if code_block_name == ("entity_start"):
                # entity节点
                node_block_new = NodeSelf()
                new_captures.append((node_block_new, "entity"))
                node_block_new.id = code_block_node.id
                node_block_new.start_byte = code_block_node.start_byte
                node_block_new.start_point = code_block_node.start_point
                node_block_new.parent = code_block_node.parent
                node_block_new.type = "entity"
                while next_index < captures_len:
                    capture_child = captures[next_index]
                    capture_child_node: Node = capture_child[0]
                    capture_child_name = capture_child[1]
                    if capture_child_name == "entity_start":
                        next_index += 1
                        continue
                    # 找到符合要求的entity_end
                    elif capture_child_name == "entity_end":
                        # 结束节点
                        node_block_new.end_byte = capture_child_node.end_byte
                        node_block_new.end_point = capture_child_node.end_point
                        next_index += 1
                        break
                    new_captures.append(capture_child)
                    next_index += 1
            elif code_block_name == ("function_start"):
                node_block_new = NodeSelf()
                new_captures.append((node_block_new, "function"))
                node_block_new.id = code_block_node.id
                node_block_new.start_byte = code_block_node.start_byte
                node_block_new.start_point = code_block_node.start_point
                node_block_new.parent = code_block_node.parent
                node_block_new.type = "function"
                while next_index < captures_len:
                    capture_child = captures[next_index]
                    capture_child_node: Node = capture_child[0]
                    capture_child_name = capture_child[1]
                    # 重复name要最后的
                    if capture_child_name == "name":
                        next_next_index = next_index + 1
                        if next_next_index < captures_len and captures[next_next_index][1] == "name":
                            # 下一个节点是name 跳过当前节点
                            next_index += 1
                            continue
                    elif capture_child_name == "function_end":
                        # 结束节点
                        if capture_child_node.start_byte != capture_child_node.end_byte:
                            # 正常结束
                            node_block_new.end_byte = capture_child_node.end_byte
                            node_block_new.end_point = capture_child_node.end_point
                            next_index += 1
                            break
                    new_captures.append(capture_child)
                    next_index += 1
            # 未考虑的起始节点
            else:
                # TODO 许可的节点 防止待解析代码块bug导致解析出错
                if code_block_name in ['import','name','entity','class','function']:
                    new_captures.append(capture)
            i = next_index
        # del captures

        return new_captures


if __name__ == "__main__":
    import time

    # 创建分割器
    chunker = AstDart()
    start_time = time.time()

    # 读取python文件到字符串
    with open(r"test-data\text\test.dart", "r", encoding="utf-8") as f:
        text_bytes = f.read()
        print(time.time() - start_time)
        start_time = time.time()
        new_chunks = chunker.chunk(text_bytes)
        # print(new_chunks)
        print(time.time() - start_time)
        start_time = time.time()
