from tree_sitter import Node
import uuid

from utils.code.ast.tree_sitter_codes import TreeSitterCodes
from utils.enum.code import CodeType

# tree_sitter_options = {
#     "query": """
#                 ;; import
#                 (call
#                     method: (identifier) @_import
#                         (#match? @_import "^(require|require_relative)$")
#                 )@import_root
#                 (call
#                     method: (identifier) @_import
#                     arguments:
#                         (argument_list
#                             (string
#                                 (string_content) @name
#                             )
#                         )
#                         (#match? @_import "^(require|require_relative)$")
#                 )
#                 ;; entity
#                 (assignment
#                     left: [
#                         (identifier) @name
#                         (instance_variable) @name
#                         (class_variable) @name
#                     ]
#                 ) @entity
#                 ;; 多entity
#                 (assignment
#                     left:(left_assignment_list
#                     (identifier)
#                     )
#                 )? @entity
#                 (assignment
#                     left:(left_assignment_list
#                     (identifier)@name
#                     )
#                 )
#                 ;; 函数
#                 (method
#                     name: (_) @name
#                 )? @function
#                 ;; 类
#                 (class
#                     name:  (constant) @name
#                 )@class
#                 ;; module
#                 (module
#                     name:  (constant) @name
#                 )@module1
#                 ;; 特殊节点
#                 """,
# }
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
                                (method  
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
                                (method  
                                    name: (_) @name 
                                )? @function
                            )
                    )
                )
                ;; 特殊节点
                """
}


class AstRuby:
    """ast分析代码"""

    def __init__(self):
        tree_sitter_languages = TreeSitterCodes("tree-sitter", "tree-sitter/source")
        self.parser = tree_sitter_languages.get_parser(CodeType.ruby)
        self.language = tree_sitter_languages.get_language(CodeType.ruby)

    def chunk(self, text: str, MAX_CHARS: int = 1500) -> list[str]:
        """按rels结构组织"""
        text_bytes = bytes(text, "utf-8")
        tree = self.parser.parse(text_bytes)
        # 查询节点
        query = self.language.query(tree_sitter_options["query"])
        captures = query.captures(tree.root_node)
        # 格式化节点内容
        code_tree: dict[str, list] = {
            "rels": [],
        }
        self.chunk_node(code_tree, captures, text_bytes, MAX_CHARS)
        return code_tree

    def chunk_node(
        self,
        code_tree,
        captures: list[list[Node, str]],
        text_bytes: bytes,
        MAX_CHARS: int = 1500,
    ):
        """
        遍历捕获的节点 每个code节点带多个子节点name
        Args:
            code_tree (dict): 存储解析结果的字典，包含 "import", "class", "function", "other" 四个类别。
            captures (list[list[Node,str]]): 待解析的节点list。
            text_bytes (str): 原始代码文本。
            MAX_CHARS (int, optional): 单个节点的最大字符数，默认为 1500。
        Returns:
            dict: 更新后的 code_tree 字典。
        """
        # 节点id与uuid对应字典
        id_uuid_dict = {}
        # 遍历捕获的节点 每个code节点带多个子节点name
        i = 0  # 初始化计数器\
        captures_len = len(captures)
        # 遍历有效代码块code_block
        while i < captures_len:
            capture = captures[i]
            code_block_node: Node = capture[0]
            code_block_name: str = capture[1]

            # 过滤无关节点
            if code_block_name.startswith("_"):
                i += 1
                continue

            # 遍历code_block包含的有效子对象 names处理
            code_child_nodes = []
            next_index = i + 1
            while next_index < captures_len:
                code_child = captures[next_index]
                code_child_node = code_child[0]
                code_child_name = code_child[1]
                if code_child_name.startswith("_"):
                    next_index += 1
                    continue
                if code_child_name != "name":
                    break
                #
                code_child_nodes.append(code_child_node)
                next_index += 1

            if code_child_nodes:
                self.chunk_node_with_name(
                    code_tree,
                    code_block_name,
                    code_block_node,
                    code_child_nodes,
                    text_bytes,
                    id_uuid_dict,
                    MAX_CHARS,
                )

            i = next_index
        
    def chunk_node_with_name(
        self,
        code_tree: dict[str, list],
        code_block_name,
        code_block_node: Node,
        code_child_nodes: list[Node],
        text_bytes: bytes,
        id_uuid_dict: dict = {},
        MAX_CHARS: int = 1500,
    ):
        """解析代码块"""
        # 获取基础节点信息
        base_node = self.check_common(code_block_node, text_bytes)
        # 当前代码块uuid
        node_block_uuid = str(uuid.uuid4())
        id_uuid_dict[code_block_node.id] = node_block_uuid
        # 查找最邻近父节点关联 从当前节点向上层查找
        node_parent_uuid = None
        while code_block_node.parent is not None:  # 递归遍历父节点
            code_block_node = code_block_node.parent
            node_parent_uuid =id_uuid_dict.get(code_block_node.id)
            if node_parent_uuid:
                # 添加父子节点关联
                code_tree["rels"].append([node_parent_uuid, node_block_uuid])
                break
        # 代码块和变量一对多(z,y =1,2)
        for code_child in code_child_nodes:
            node_child_uuid = str(uuid.uuid4())
            code_child_current = {
                "name": text_bytes[code_child.start_byte : code_child.end_byte].decode(
                    "utf-8"
                ),
                "uuid": node_child_uuid,
                "block_uuid":node_block_uuid,
                "def_position_range": list(
                    code_child.start_point + code_child.end_point
                ),
            }
            node_all_current = base_node | code_child_current
            if code_block_name not in code_tree:
                code_tree[code_block_name] = []
            code_tree[code_block_name].append(node_all_current)

    def check_common(self, code_block_node: Node, text_bytes):
        node_current = {
            "byte_range": [code_block_node.start_byte, code_block_node.end_byte],
            "position_range": list(code_block_node.start_point + code_block_node.end_point),
            "code": text_bytes[code_block_node.start_byte : code_block_node.end_byte].decode("utf-8"),
            "size": code_block_node.end_byte - code_block_node.start_byte,
            # 真实类型  匹配时默认将struct module等视为class
            "real_type":code_block_node.type
        }
        return node_current


if __name__ == "__main__":
    import time

    # 创建分割器
    chunker = AstRuby()
    start_time = time.time()

    # 读取python文件到字符串
    # with open(r"temp\me\address\AddressBookDetail.Ruby", "r", encoding="utf-8") as f:
    # with open(r"test-data\text\test.Ruby", "r", encoding="utf-8") as f:
    with open(r"test-data\text\test.rb", "r", encoding="utf-8") as f:
        text_bytes = f.read()
        print(time.time() - start_time)
        start_time = time.time()
        new_chunks = chunker.chunk(text_bytes)
        # print(new_chunks)
        print(time.time() - start_time)
        start_time = time.time()
