import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Node


class AstPython:
    def __init__(self):
        self.parser = Parser(Language(tspython.language()))

    # def chunk_node(self, node: Node, text: str, MAX_CHARS: int = 1500) -> list[str]:
    #     """
    #     将给定的树节点（Node）表示的文本分割成多个不超过指定最大字符数的块。

    #     参数:
    #     - node (Node): 树节点对象，通常由 tree-sitter 解析器生成。
    #     - text (str): 原始文本字符串，包含整个文档的内容。
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
    #             new_chunks.extend(self.chunk_node(child, text, MAX_CHARS))
    #         # 下一个子节点太大，我们递归地对子节点进行 chunk 并将其添加到 chunk 列表中
    #         elif len(current_chunk) + child.end_byte - child.start_byte > MAX_CHARS:
    #             new_chunks.append(current_chunk)
    #             current_chunk = text[child.start_byte : child.end_byte]
    #         # 将当前块与子节点连接
    #         else:
    #             current_chunk += text[child.start_byte : child.end_byte]
    #     return new_chunks

    def chunk(self, text: str, MAX_CHARS: int = 1500) -> list[str]:
        tree = self.parser.parse(bytes(text, "utf-8"))
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

        code_tree = self.chunk_node(code_tree, tree.root_node, text, MAX_CHARS)
        return code_tree

    def chunk_node(self, code_tree, node: Node, text: str, MAX_CHARS: int = 1500):
        for child in node.children:
            # 解析字段所在文件位置
            node_current = {"byte_range": [child.start_byte, child.end_byte]}
            # 节点类型
            type_code = child.type
            
            if type_code == "import_statement":
                # TODO 解析导入
                node_current["code"] = text[child.start_byte : child.end_byte]
                code_tree["import"].append(node_current)

            elif type_code == "import_from_statement":
                node_current["code"] = text[child.start_byte : child.end_byte]
                code_tree["import"].append(node_current)

            elif type_code == "class_definition":
                node_current["name"] = ""
                node_current["function"] = []
                # class内部解析 只考虑一层fuc
                for class_child in child.children:
                    if class_child.type == "identifier":
                        node_current["name"] = text[class_child.start_byte : class_child.end_byte]
                        # 参数  实现接口
                    elif class_child.type == 'argument_list':
                        node_current["argument_list"] = text[class_child.start_byte+1 : class_child.end_byte-1]
                    if class_child.type == "block":
                        for fuc_child in class_child.children:
                            if fuc_child.type == "function_definition":
                                self.chunk_node_fuc(node_current, fuc_child, text)
                code_tree["class"].append(node_current)

            elif type_code == "function_definition":
                self.chunk_node_fuc(code_tree, child, text)

            else:
                # 未考虑到的放在一起
                node_current["code"] = text[child.start_byte : child.end_byte]
                node_current["type"] = type_code
                code_tree["other"].append(node_current)
        return code_tree

    def chunk_node_fuc(self, code_tree, node: Node, text: str):
        """解析function节点"""
        code = text[node.start_byte : node.end_byte]
        size = len(code)
        node_current = {
            "byte_range": [node.start_byte, node.end_byte],
            "code": code,
            # 函数需要大小 方便后续解析
            "size": size,
            'name':'',
            'return_type':'',
            
        }
        for fuc_child in node.children:
            if fuc_child.type == "identifier":
                node_current["name"] = text[fuc_child.start_byte : fuc_child.end_byte]
                # 参数  实现接口
            elif fuc_child.type == 'parameters':
                node_current["parameters"] = text[fuc_child.start_byte+1 : fuc_child.end_byte-1]
            elif fuc_child.type == 'type':
                node_current["return_type"] = text[fuc_child.start_byte : fuc_child.end_byte]
        code_tree["function"].append(node_current)

    def chunk_simple(
        self, text: str, MAX_CHARS: int = 1500, overlap: int = 0, chunk_size: int = 10
    ) -> list[str]:
        """
        将给定的文本按行分割成多个块，每个块的字符数不超过指定的最大字符数。

        参数:
        - text (str): 需要分割的原始文本。
        - MAX_CHARS (int): 每个块的最大字符数，默认为1500。
        - overlap (int): 块之间的重叠行数，默认为0。
        - chunk_size (int): 每个块包含的行数，默认为10。

        返回:
        - list[str]: 包含分割后的文本块的列表。
        """
        source_lines = text.split("\n")
        num_lines = len(source_lines)
        chunks = []
        start_line = 0
        while start_line < num_lines and num_lines > overlap:
            end_line = min(start_line + chunk_size, num_lines)
            chunk = "\n".join(source_lines[start_line:end_line])
            chunks.append(chunk)
            start_line += chunk_size - overlap
            return chunks



Node

if __name__ == "__main__":
    # 创建分割器
    chunker = AstPython()

    # 读取python文件到字符串
    with open(r"D:\test\fastapi\routing.py", "r", encoding="utf-8") as f:
        text = f.read()
        new_chunks = chunker.chunk(text)
        print(new_chunks)
