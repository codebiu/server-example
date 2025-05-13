from abc import ABC, abstractmethod
import uuid
from config.index import tree_sitter_use_build_path

class Analysis(ABC):
    """AST分析代码的基类"""

    @abstractmethod
    def __init__(self):
        """初始化，存储项目中的类信息"""
        self.tree_sitter_use_build_path = tree_sitter_use_build_path
        self.project_tree = {}  # 项目类信息字典
        self.node_param = ["type"]  # 节点附加参数列表  ast时添加到节点属性中
        self.node_params = []  # 节点附加参数列表  ast时添加到节点属性中
        self.node_delete = ['class_body'] # 节点内容父节点删除
        self.code_tree_list = []  # 代码树列表
        self.class_function_entity_all_set = set()  # 类函数实体字典
        self.rels_uuid_list = []  # 所有调用关系
        self.extend_uuid_list = []  # 所有继承关系
        self.impl_uuid_list = []  # 所有实现的关系
        self.class_name_extend_name_dict = {}
        self.impl_name_interface_name_dict = {}

    def chunk_base(self, text: str, max_chars: int = 1500) -> dict:
        """拆分单个文件的代码

        Args:
            text: 代码文本
            max_chars: 单个节点的最大字符数

        Returns:
            解析后的代码树结构
        """
        text_bytes = bytes(text, "utf-8")
        tree = self.parser.parse(text_bytes)  # 解析为AST
        captures = self.query.captures(tree.root_node)  # 捕获AST节点
        captures_new = self._process_captures(captures, text_bytes)  # 处理捕获节点

        # 初始化代码树
        code_tree = {
            "rels_main": [],  # 主要节点关系 类 函数 实体
            "roots_main": [],  # 主要根节点
            "rels": [],  # 所有节点关系
            "roots": [],  # 所有根节点 包含import等
            "uuid_map": {},  # UUID到节点映射
            "id_map": {},  # 节点ID到UUID映射
            "child_map": {},  # 父子关系映射
            "tree": {},  # 单文件内代码解析出的节点树结构
        }
        self._parse_nodes(code_tree, captures_new, text_bytes, max_chars)  # 解析节点
        self.code_tree_list.append(code_tree)  # 添加到代码树列表
        return code_tree

    def _process_captures(self, captures, text_bytes):
        """过滤处理捕获节点"""
        return captures  # 默认直接返回

    def _parse_nodes(self, code_tree, captures, text_bytes, max_chars):
        """遍历捕获节点，解析代码块及其子节点"""
        i = 0
        n = len(captures)

        while i < n:
            node, name = captures[i]  # 当前节点和名称

            # 收集子节点和附加信息
            child_nodes = []
            extra_info = {}
            extra_info_dict = {}
            extra_delete_list = []
            next_idx = i + 1
            while next_idx < n:
                child, child_name = captures[next_idx]
                if child_name == "name":
                    child_nodes.append(child)
                elif child_name in self.node_param:
                    extra_info[child_name] = child
                elif child_name in self.node_params:
                    extra_info_dict.setdefault(child_name, []).append(child)
                elif child_name in self.node_delete:
                    extra_delete_list.append(child)
                else:
                    break
                next_idx += 1

            if child_nodes:  # 处理有子节点的代码块
                try:
                    self._parse_single_node(
                        code_tree,
                        name,
                        node,
                        child_nodes,
                        extra_info,
                        extra_info_dict,
                        extra_delete_list,
                        text_bytes,
                        max_chars,
                    )
                except Exception as e:
                    print("AST节点解析错误:", e)

            i = next_idx

    def _parse_single_node(
        self,
        code_tree,
        node_type,
        node,
        children,# 子节点 类名函数名所在代码块
        extra_info,
        extra_info_dict,
        extra_delete_list,
        text_bytes,
        max_chars,
    ):
        """解析单个代码块节点"""
        # 获取基础信息
        base_info = self._get_node_info(node, node_type, text_bytes,extra_delete_list)

        # 初始化节点ID映射
        id_map = code_tree["id_map"].setdefault(node.id, [])

        # 处理附加信息
        extra = {}
        for key, info_node in extra_info.items():
            extra[key] = text_bytes[info_node.start_byte : info_node.end_byte].decode(
                "utf-8"
            )
        # 处理附加节点信息
        extras = {}
        for key, info_nodes in extra_info_dict.items():
            for info_node_this in info_nodes:
                info_this_dict = {
                    "_use_type": info_node_this.type,
                    "code": text_bytes[
                        info_node_this.start_byte : info_node_this.end_byte
                    ].decode("utf-8"),
                    "position_range": list(info_node_this.start_point + info_node_this.end_point),
                }
                extras.setdefault(key, []).append(info_this_dict)
        # 代码块一对多(z,y =1,2)
        for child in children:
            node_uuid = str(uuid.uuid4())  # 生成唯一ID

            # 构建子节点信息
            child_info = {
                "name": text_bytes[child.start_byte : child.end_byte].decode("utf-8"),
                "uuid": node_uuid,
                "def_position_range": list(child.start_point + child.end_point),
            }

            # 合并节点信息
            node_info = base_info | child_info | extra | extras

            # 添加到代码树
            code_tree.setdefault(node_type, []).append(node_info)
            code_tree["uuid_map"][node_uuid] = node_info
            id_map.append(node_uuid)

            # 查找父节点
            parent = node.parent
            parent_uuids = None
            while parent is not None:
                parent_uuids = code_tree["id_map"].get(parent.id, [])
                if parent_uuids:
                    break
                parent = parent.parent

            if parent_uuids:  # 建立父子关系
                for parent_uuid in parent_uuids:
                    code_tree["rels"].append([parent_uuid, node_uuid])
                    # rels_main
                    if node_type in ["class", "function", "entity"]:
                        code_tree["rels_main"].append([parent_uuid, node_uuid])
                    code_tree["child_map"].setdefault(parent_uuid, []).append(node_info)
            else:  # 标记为根节点
                code_tree["roots"].append(node_uuid)
                # roots_main
                if node_type in ["class", "function", "entity"]:
                    code_tree["roots_main"].append(node_uuid)

    def _get_node_info(self, node, node_type, text_bytes,extra_delete_list):
        node_info_base = {
            "byte_range": [node.start_byte, node.end_byte],
            "position_range": list(node.start_point + node.end_point),
            "size": node.end_byte - node.start_byte,
            "node_type": node_type,
            "_use_type": node.type,
        }
        # 类和接口处理
        if extra_delete_list:
            for delete_node in extra_delete_list:
                node_info_base["code"] = text_bytes[node.start_byte : delete_node.start_byte].decode("utf-8")
                # +'{}'
        else:
            node_info_base["code"] = text_bytes[node.start_byte : node.end_byte].decode("utf-8")
        """所有节点基础信息获取"""
        return node_info_base

    def chunk_project(self,help_info):
        """解析所有代码元素关系"""
        # 文件内全变量名构建,建立元素间关系
        pass

if __name__ == "__main__":
    pass
