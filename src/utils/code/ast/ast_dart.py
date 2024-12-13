import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Node

from tree_sitter_codes import TreeSitterCodes
from utils.enum.code import CodeType

class TreeSitterDartType():
    import_type = 'import_or_export'
    class_type = 'class_definition'
    class_super_type = 'superclass'
    fuc_type = 'function_signature'
    fuc_params_type = 'formal_parameter_list'
    call_type = 'identifier'
    
class AstDart:
    """ast分析代码"""

    def __init__(self):
        tree_sitter_languages = TreeSitterCodes("tree-sitter", "tree-sitter")
        self.parser = tree_sitter_languages.get_parser(CodeType.dart)

    def chunk(self, text: str, MAX_CHARS: int = 1500) -> list[str]:
        text_bytes = bytes(text, "utf-8")
        tree = self.parser.parse(text_bytes)
        # 格式化节点内容
        code_tree = {
            "import": [
                # {"import_path": "", "import_obj": []}
            ],
            "class": [
                # {
                #     "name": "",
                #     # 类内func
                #     "function": [{"call": []}],
                # }
            ],
            # 独立func
            "function": [
                # {"call": []}
            ],
            "other": [],
        }
        code_tree = self._chunk_node(code_tree, tree.root_node, text_bytes, MAX_CHARS)
        return code_tree

    def _chunk_node(
        self, code_tree, node: Node, text_bytes: bytes, MAX_CHARS: int = 1500
    ):
        """
        递归解析节点,分离出import, class, function, other
        Args:
            code_tree (dict): 存储解析结果的字典，包含 "import", "class", "function", "other" 四个类别。
            node (Node): 当前解析的节点。
            text_bytes (str): 原始代码文本。
            MAX_CHARS (int, optional): 单个节点的最大字符数，默认为 1500。

        Returns:
            dict: 更新后的 code_tree 字典。
        """

        for i in range(node.child_count):
            child = node.child(i)
            # 解析字段所在文件位置
            node_current = {"byte_range": [child.start_byte, child.end_byte]}
            # 节点类型
            type_code = child.type

            if type_code == TreeSitterDartType.import_type:
                # TODO 解析导入 考虑三方库和本地实现
                # node_current["code"] = text_bytes[child.start_byte : child.end_byte].decode('utf-8')
                code_tree["import"].append(
                    text_bytes[child.start_byte : child.end_byte].decode("utf-8")
                )
            elif type_code == TreeSitterDartType.class_type:
                node_current = self._chunk_node_class(child, text_bytes)
                code_tree["class"].append(node_current)
            # 装饰器 todo
            elif type_code == "decorated_definition":
                self._chunk_node(code_tree, child, text_bytes, MAX_CHARS)
            # 函数
            elif type_code == "method_signature" or type_code == TreeSitterDartType.fuc_type:
                node_function_body = node.child(i + 1)
                if type_code == "method_signature":
                    child = child.child(0)
                node_current = self._chunk_node_fuc(
                    child, node_function_body, text_bytes
                )
                code_tree["function"].append(node_current)
            else:
                # 未考虑到的放在一起
                self._chunk_node_other(code_tree, child, text_bytes)
        return code_tree

    def _chunk_node_class(self, node: Node, text_bytes: bytes, MAX_CHARS: int = 1500):
        """解析class节点"""
        node_current = {
            "name": "",
            "byte_range": [node.start_byte, node.end_byte],
            # 继承 实现 接口
            "argument_list": "",
            # 代码注释
            "class_string": [],
            # 代码赋值 单个变量
            "assignment": [],
            # 包含的函数
            "function": [],
        }
        # class内部解析 只考虑一层fuc
        for child in node.children:
            if child.type == "identifier":
                node_current["name"] = text_bytes[
                    child.start_byte : child.end_byte
                ].decode("utf-8")
                # 参数  实现接口
            elif (
                child.type ==  TreeSitterDartType.class_super_type
                or child.type == "interfaces"
                or child.type == "arguments"
            ):
                node_current["argument_list"] = text_bytes[
                    child.start_byte : child.end_byte - 1
                ].decode("utf-8")
            elif child.type == "class_body" or child.type == "block":
                # for child_child in child.children:
                for i in range(child.child_count):
                    child_child = child.child(i)
                    if child_child.type == "expression_statement":
                        # 处理类内变量和注释
                        self._chunk_node_expression_statement(
                            node_current,
                            child_child,
                            text_bytes,
                        )
                    # function_definition
                    elif (
                        child_child.type == "method_signature"
                        or child_child.type == TreeSitterDartType.fuc_type
                    ):
                        node_function_body = child.child(i + 1)
                        if child_child.type == "method_signature":
                            # function_signature获取
                            child_child = child_child.child(0)
                        node_child_current = self._chunk_node_fuc(
                            child_child, node_function_body, text_bytes
                        )
                        node_current["function"].append(node_child_current)
        return node_current

    def _chunk_node_fuc(self, node: Node, node_function_body: Node, text_bytes: bytes):
        """解析function节点"""
        code = text_bytes[node.start_byte : node.end_byte].decode("utf-8")
        size = len(code)
        node_current = {
            "name": "",
            "byte_range": [node.start_byte, node.end_byte],
            "code": code,
            # 函数需要大小 方便后续解析
            "size": size,
            "return_type": "",
            "call": set(),
        }
        for fuc_child in node.children:
            if fuc_child.type == "identifier":
                node_current["name"] = text_bytes[
                    fuc_child.start_byte : fuc_child.end_byte
                ].decode("utf-8")
            # 参数  实现接口
            elif fuc_child.type == TreeSitterDartType.fuc_params_type:
                node_current["parameters"] = text_bytes[
                    fuc_child.start_byte + 1 : fuc_child.end_byte - 1
                ].decode("utf-8")
            # 返回值
            elif fuc_child.type == "void_type" or fuc_child.type == "type_identifier":
                node_current["return_type"] = text_bytes[
                    fuc_child.start_byte : fuc_child.end_byte
                ].decode("utf-8")
        # 函数体
        if node_function_body:
            call_child = self._chunk_node_call(node_function_body, text_bytes)
            node_current["call"] = node_current["call"] | call_child
        # 所有调用函数
        node_current["call"] = list(node_current["call"])
        return node_current

    def _chunk_node_call(self, node: Node, text_bytes: bytes, MAX_CHARS: int = 1500):
        """递归节点下所有调用函数"""
        call = set()
        for child in node.children:
            if child.type == TreeSitterDartType.call_type:
                fuc_name = text_bytes[child.start_byte : child.end_byte].decode("utf-8")
                call.add(fuc_name)
            else:
                call_child = self._chunk_node_call(child, text_bytes)
                # 合并
                call = call | call_child
        return call

    def _chunk_node_expression_statement(
        self, node_expression_statement, node: Node, text_bytes: bytes
    ):
        """解析expression_statement节点"""
        # 只考虑assignment string
        for child in node.children:
            if child.type == "string":
                node_expression_statement["class_string"].append(
                    text_bytes[child.start_byte : child.end_byte].decode("utf-8")
                )
            elif child.type == "assignment":
                node_expression_statement["assignment"].append(
                    text_bytes[child.start_byte : child.end_byte].decode("utf-8")
                )

    def _chunk_node_other(
        self, code_tree, node: Node, text_bytes: bytes, MAX_CHARS: int = 1500
    ):
        code_tree["other"].append(
            text_bytes[node.start_byte : node.end_byte].decode("utf-8")
        )

    def chunk_simple(
        self,
        text_bytes: bytes,
        MAX_CHARS: int = 1500,
        overlap: int = 0,
        chunk_size: int = 10,
    ) -> list[str]:
        """
        将给定的文本按行分割成多个块，每个块的字符数不超过指定的最大字符数。

        参数:
        - text_bytes (str): 需要分割的原始文本。
        - MAX_CHARS (int): 每个块的最大字符数，默认为1500。
        - overlap (int): 块之间的重叠行数，默认为0。
        - chunk_size (int): 每个块包含的行数，默认为10。

        返回:
        - list[str]: 包含分割后的文本块的列表。
        """
        source_lines = text_bytes.split("\n")
        num_lines = len(source_lines)
        chunks = []
        start_line = 0
        while start_line < num_lines and num_lines > overlap:
            end_line = min(start_line + chunk_size, num_lines)
            chunk = "\n".join(source_lines[start_line:end_line])
            chunks.append(chunk)
            start_line += chunk_size - overlap
            return chunks


if __name__ == "__main__":
    import time

    # 创建分割器
    chunker = AstDart()
    start_time = time.time()

    # 读取python文件到字符串
    # with open(r"temp\me\address\AddressBookDetail.dart", "r", encoding="utf-8") as f:
    with open(r"test-data\text\test.dart", "r", encoding="utf-8") as f:
        text_bytes = f.read()
        print(time.time() - start_time)
        start_time = time.time()
        new_chunks = chunker.chunk(text_bytes)
        # print(new_chunks)
        print(time.time() - start_time)
        start_time = time.time()
