import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Node


class AstPython:
    """ast分析代码"""

    def __init__(self):
        self.parser = Parser(Language(tspython.language()))

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
        code_tree = self.chunk_node(code_tree, tree.root_node, text_bytes, MAX_CHARS)
        return code_tree

    def chunk_node(
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

        for child in node.children:
            # 解析字段所在文件位置
            node_current = {"byte_range": [child.start_byte, child.end_byte]}
            # 节点类型
            type_code = child.type

            if type_code == "import_statement":
                # TODO 解析导入 考虑三方库和本地实现
                # node_current["code"] = text_bytes[child.start_byte : child.end_byte].decode('utf-8')
                code_tree["import"].append(
                    text_bytes[child.start_byte : child.end_byte].decode("utf-8")
                )

            elif type_code == "import_from_statement":
                # node_current["code"] = text_bytes[child.start_byte : child.end_byte].decode('utf-8')
                code_tree["import"].append(
                    text_bytes[child.start_byte : child.end_byte].decode("utf-8")
                )

            elif type_code == "class_definition":
                node_current = self.chunk_node_class(child, text_bytes)
                code_tree["class"].append(node_current)
            # 装饰器 todo
            elif type_code == "decorated_definition":
                self.chunk_node(code_tree, child, text_bytes, MAX_CHARS)
            elif type_code == "function_definition":
                node_current = self.chunk_node_fuc(child, text_bytes)
                code_tree["function"].append(node_current)
            else:
                # 未考虑到的放在一起
                self.chunk_node_other(code_tree,child,text_bytes)
        return code_tree

    def chunk_node_class(self, node: Node, text_bytes: bytes, MAX_CHARS: int = 1500):
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
            elif child.type == "argument_list":
                node_current["argument_list"] = text_bytes[
                    child.start_byte + 1 : child.end_byte - 1
                ].decode("utf-8")
            elif child.type == "block":
                for child_child in child.children:
                    if child_child.type == "expression_statement":
                        # 处理类内变量和注释
                        self.chunk_node_expression_statement(
                            node_current,
                            child_child,
                            text_bytes,
                        )
                    if child_child.type == "function_definition":
                        node_child_current = self.chunk_node_fuc(
                            child_child, text_bytes
                        )
                        node_current["function"].append(node_child_current)
        return node_current

    def chunk_node_fuc(self, node: Node, text_bytes: bytes):
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
            elif fuc_child.type == "parameters":
                node_current["parameters"] = text_bytes[
                    fuc_child.start_byte + 1 : fuc_child.end_byte - 1
                ].decode("utf-8")
            elif fuc_child.type == "type":
                node_current["return_type"] = text_bytes[
                    fuc_child.start_byte : fuc_child.end_byte
                ].decode("utf-8")
            elif fuc_child.type == "block":
                call_child = self.chunk_node_call(fuc_child, text_bytes)
                node_current["call"] = node_current["call"] | call_child
        # 所有调用函数
        node_current["call"] = list(node_current["call"])
        return node_current

    def chunk_node_call(self, node: Node, text_bytes: bytes, MAX_CHARS: int = 1500):
        """递归节点下所有调用函数"""
        call = set()
        for child in node.children:
            if child.type == "call":
                for call_child in child.children:
                    # 带类函数
                    if (
                        call_child.type == "attribute"
                        or call_child.type == "identifier"
                    ):
                        fuc_name = text_bytes[
                            call_child.start_byte : call_child.end_byte
                        ].decode("utf-8")
                        call.add(fuc_name)
            else:
                call_child = self.chunk_node_call(child, text_bytes)
                # 合并
                call = call | call_child
        return call

    def chunk_node_expression_statement(
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


    def chunk_node_other(self,code_tree, node: Node, text_bytes: bytes, MAX_CHARS: int = 1500):
        code_tree["other"].append(text_bytes[ node.start_byte : node.end_byte ].decode("utf-8"))
        
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

    # def chunk_node(self, node: Node, text_bytes: bytes, MAX_CHARS: int = 1500) -> list[str]:
    #     """
    #     将给定的树节点（Node）表示的文本分割成多个不超过指定最大字符数的块。

    #     参数:
    #     - node (Node): 树节点对象，通常由 tree-sitter 解析器生成。
    #     - text_bytes (str): 原始文本字符串，包含整个文档的内容。
    #     - MAX_CHARS (int): 每个块的最大字符数，默认值为 1500。

    #     返回:
    #     - list[str]: 包含分割后的文本块的列表。
    #     """
    #     new_chunks = []
    #     current_chunk = ""
    #     for child in node.children:
    #         # 当前 chunk 太大，我们将其添加到我们的 chunk 列表中并清空 bundle
    #         if child.end_byte - child.start_byte > MAX_CHARS:
    #             new_chunks.append(current_chunk)
    #             current_chunk = ""
    #             new_chunks.extend(self.chunk_node(child, text_bytes, MAX_CHARS))
    #         # 下一个子节点太大，我们递归地对子节点进行 chunk 并将其添加到 chunk 列表中
    #         elif len(current_chunk) + child.end_byte - child.start_byte > MAX_CHARS:
    #             new_chunks.append(current_chunk)
    #             current_chunk = text_bytes[child.start_byte : child.end_byte]
    #         # 将当前块与子节点连接
    #         else:
    #             current_chunk += text_bytes[child.start_byte : child.end_byte]
    #     return new_chunks


if __name__ == "__main__":
    import time

    # 创建分割器
    chunker = AstPython()
    start_time = time.time()

    # 读取python文件到字符串
    with open(r"D:\test\fastapi\routing.py", "r", encoding="utf-8") as f:
        text_bytes = f.read()
        print(time.time() - start_time)
        start_time = time.time()
        new_chunks = chunker.chunk(text_bytes)
        # print(new_chunks)
        print(time.time() - start_time)
        start_time = time.time()
