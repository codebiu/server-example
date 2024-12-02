
class GraphTraversal:
    def __init__(self, node_get, get_children, has_child=None) -> None:
        self.node_get = node_get
        self.get_children = get_children
        if has_child is not None:
            self.has_child = has_child
        else:
            self.has_child = lambda node: self.get_children(node) is not None
            

    def preorder_traversal(self, node_root):
        """前序遍历图"""
        for child in self.get_children(node_root):
            # 节点 根
            if self.has_child(child):
                self.node_get(node_root, child)
            # 叶节点
            else:
                pass

        return

    def build_directory_tree(root_path, root_path_this=None):
        tree = []
        size = 0
        if root_path_this is None:
            root = Path(root_path)
        else:
            root = Path(root_path_this)
        for item in root.iterdir():
            tree_node = {}
            tree.append(tree_node)
            tree_node["label"] = item.name
            # 获取子目录相对于父目录的路径
            relative_path = item.relative_to(root_path)
            tree_node["path"] = str(relative_path)
            # 如果是目录，则递归构建子树
            if item.is_dir():
                tree_node["children"], tree_node["size"] = (
                    DirectoryTree.build_directory_tree(root_path, item)
                )
            # 如果是文件，则直接添加到树中
            else:
                # st_size: 文件的大小，以字节为单位。
                # st_mtime: 文件的最后修改时间，以时间戳表示。
                # st_ctime: 文件的创建时间，以时间戳表示（在 Unix 系统上，这可能是指元数据的最后更改时间）。
                # st_atime: 文件的最后访问时间，以时间戳表示。
                tree_node_stat = item.stat()
                tree_node["size"] = tree_node_stat.st_size
            size += tree_node["size"]
        return tree, size