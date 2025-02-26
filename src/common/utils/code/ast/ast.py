from abc import ABC, abstractmethod
from tree_sitter import Node
from common.utils.enum.code import CodeType
from tree_sitter_codes import TreeSitterCodes
import uuid

tree_sitter_options = {
    "query": """
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
                """
}

class Ast(ABC):
    """ast分析代码"""
    @abstractmethod
    def __init__(self):
        pass
        # tree_sitter_languages = TreeSitterCodes("tree-sitter", "tree-sitter/source")
        # self.parser = tree_sitter_languages.get_parser(CodeType.ruby)
        # self.language = tree_sitter_languages.get_language(CodeType.ruby)
        # self.tree_sitter_options = tree_sitter_options
        # self.query = self.language.query(tree_sitter_options["query"])
        
        
    def chunk(self, text: str, MAX_CHARS: int = 1500) -> list[str]:
        """按rels结构组织"""
        text_bytes = bytes(text, "utf-8")
        tree = self.parser.parse(text_bytes)
        # 查询节点
        captures = self.query.captures(tree.root_node)

        captures_new =self._captures_deal(captures,text_bytes)
        # 格式化节点内容
        code_tree: dict[str, list] = {
            "rels": [],
            "roots": [],
        }
        self.chunk_nodes(code_tree, captures_new, text_bytes, MAX_CHARS)
        return code_tree
    
    def _captures_deal(self,captures,text_bytes):
        """过滤修改节点"""    
        return captures


    def chunk_nodes(
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
        id_uuid_dict_parent = {}
        # 遍历捕获的节点 每个code节点带多个子节点name
        i = 0  # 初始化计数器\
        captures_len = len(captures)
        # 遍历有效代码块code_block
        while i < captures_len:
            capture = captures[i]
            code_block_node: Node = capture[0]
            code_block_name: str = capture[1]

            # 遍历code_block包含的有效子对象 names处理
            code_child_nodes = []
            next_index = i + 1
            while next_index < captures_len:
                code_child = captures[next_index]
                code_child_node = code_child[0]
                code_child_name = code_child[1]
                if code_child_name != "name":
                    break
                code_child_nodes.append(code_child_node)
                next_index += 1
            if code_child_nodes:
                self.chunk_node_with_name(
                    code_tree,
                    code_block_name,
                    code_block_node,
                    code_child_nodes,
                    text_bytes,
                    id_uuid_dict_parent,
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
        id_uuid_dict_parent: dict = {},
        MAX_CHARS: int = 1500,
    ):
        """解析单个节点代码块"""
        # 获取基础节点信息
        base_node = self.check_common(code_block_node,code_block_name, text_bytes)
        # 查找最邻近父节点关联 从当前节点向上层查找
        node_parent_uuid = None
        node_block_uuid = None
        # node_parent = None
        # node_block = None
        code_block_parent = code_block_node.parent
        while code_block_parent is not None:  # 递归遍历父节点
            # node_parent = id_uuid_dict_parent.get(code_block_parent.id)
            node_parent_uuid = id_uuid_dict_parent.get(code_block_parent.id)
            if node_parent_uuid:
            # if node_parent:
                break
            code_block_parent = code_block_parent.parent

        # 代码块和变量一对多(z,y =1,2)
        for code_child in code_child_nodes:
            node_block_uuid = str(uuid.uuid4())
            code_child_current = {
                "name": text_bytes[code_child.start_byte : code_child.end_byte].decode(
                    "utf-8"
                ),
                "uuid": node_block_uuid,
                "def_position_range": list(
                    code_child.start_point + code_child.end_point
                ),
            }
            node_block = base_node | code_child_current
            if code_block_name not in code_tree:
                code_tree[code_block_name] = []
            code_tree.get(code_block_name).append(node_block)
            # 关系
            # if node_parent:
            if node_parent_uuid:
                # 添加父子节点关联
                code_tree.get("rels").append([node_parent_uuid,node_block_uuid])
                # code_tree.get("rels").append([node_parent,node_block])
            else:
                # 添加根节点
                code_tree.get("roots").append(node_block_uuid)
                # code_tree.get("roots").append(node_block)
            
        # 父节点代码块对应一个uuid
        # id_uuid_dict_parent[code_block_node.id] = node_block
        id_uuid_dict_parent[code_block_node.id] = node_block_uuid

    def check_common(self, code_block_node: Node,code_block_name, text_bytes):
        node_current = {
            "byte_range": [code_block_node.start_byte, code_block_node.end_byte],
            "position_range": list(
                code_block_node.start_point + code_block_node.end_point
            ),
            "code": text_bytes[
                code_block_node.start_byte : code_block_node.end_byte
            ].decode("utf-8"),
            "size": code_block_node.end_byte - code_block_node.start_byte,
            # 真实类型  匹配时默认将struct module等视为class
            "node_type": code_block_name,
            "_use_type": code_block_node.type,
        }
        return node_current
    

if __name__ == "__main__":
    import time

    # # 创建分割器
    # chunker = AstRuby()
    # start_time = time.time()

    # # 读取python文件到字符串
    # # with open(r"temp\me\address\AddressBookDetail.Ruby", "r", encoding="utf-8") as f:
    # # with open(r"test-data\text\test.Ruby", "r", encoding="utf-8") as f:
    # with open(r"test-data\text\main.rb", "r", encoding="utf-8") as f:
    #     text_bytes = f.read()
    #     print(time.time() - start_time)
    #     start_time = time.time()
    #     new_chunks = chunker.chunk(text_bytes)
    #     # print(new_chunks)
    #     print(time.time() - start_time)
    #     start_time = time.time()
