from pathlib import Path
import json


class DirectoryTree:
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

    def build_directory_list(root_path, root_path_this=None, list: list = []):
        size = 0
        if root_path_this is None:
            root = Path(root_path)
        else:
            root = Path(root_path_this)
        for item in root.iterdir():
            list_node = {}
            list.append(list_node)
            list_node["label"] = item.name
            # 获取子目录相对于父目录的路径
            relative_path = item.relative_to(root_path)
            list_node["path"] = str(relative_path)
            # 如果是目录，则递归插入
            if item.is_dir():
                list_node["type"] = "Folder"
                temp, list_node["size"] = DirectoryTree.build_directory_list(
                    root_path, item, list
                )
            # 如果是文件，则直接添加到树中
            else:
                list_node["type"] = "File"
                # st_size: 文件的大小，以字节为单位。
                # st_mtime: 文件的最后修改时间，以时间戳表示。
                # st_ctime: 文件的创建时间，以时间戳表示（在 Unix 系统上，这可能是指元数据的最后更改时间）。
                # st_atime: 文件的最后访问时间，以时间戳表示。
                list_node_stat = item.stat()
                list_node["size"] = list_node_stat.st_size
            size += list_node["size"]
        return list, size

    def build_dirFile_level_one(self, root_path):
        tree = []
        root = Path(root_path)
        for item in root.iterdir():
            tree_node = {}
            tree.append(tree_node)
            # 如果是目录，则递归构建子树
            if item.is_dir():
                tree_node["d"] = item.name
            else:
                tree_node["f"] = item.name
                tree_node_stat = item.stat()
                tree_node["size"] = tree_node_stat.st_size
        return tree

    def build_directory_tree_root(root_path, tree=None):
        root_path = Path(root_path)
        node = {"label": root_path.name, "path": str(root_path), "children": []}
        # 非首级节点
        if tree is not None:
            tree["children"].append(node)
        tree = node

        for item in root_path.iterdir():
            if item.is_dir():
                DirectoryTree.build_directory_tree_obj(item, tree)
            else:
                file_node = {"label": item.name, "path": str(item)}
                tree["children"].append(file_node)
        return tree

    def build_directory_list_root(root_path,root_path_this=None,node_parent=None):
        '''遍历文件获取属性和关系'''
        list_all = []
        # root_path_this 为了有root_path 截取部分路径
        if root_path_this is None:
            root_path = Path(root_path)
            root_path_this = root_path

        relative_path = root_path_this.relative_to(root_path.parent).parent.parts
        # 当前文件夹节点
        node_this = {"label": root_path_this.name, "path": list(relative_path), "type": "Folder","size":0}
        list_all.append(node_this)
        for item in root_path_this.iterdir():
            if item.is_dir():
                lsit_new = DirectoryTree.build_directory_list_root(root_path,item,node_this)
                list_all.extend(lsit_new)
            else:
                list_node_stat = item.stat()
                size_file = list_node_stat.st_size
                relative_path = item.relative_to(root_path.parent).parent.parts
                node_file = {
                    "label": item.name,
                    "path": list(relative_path),
                    "type": "File",
                    "size": size_file,
                }
                list_all.append(node_file)
                node_this["size"] += size_file
        # 文件夹内属性累加
        if node_parent is not None:
            node_parent["size"] += node_this["size"]
        return list_all
    
    # def build_directory_list_root(root_path):
    #     list = []
    #     size = 0
    #     root_path = Path(root_path)
    #     # 当前文件夹节点
    #     node_this = {"label": root_path.name, "path": str(root_path), "type": "Folder"}
    #     list.append(node_this)
    #     for item in root_path.iterdir():
    #         size_new = 0
    #         if item.is_dir():
    #             lsit_new, size_new = DirectoryTree.build_directory_list_root(item)
    #             list.extend(lsit_new)
    #         else:
    #             list_node_stat = item.stat()
    #             size_new = list_node_stat.st_size
    #             node_file = {
    #                 "label": item.name,
    #                 "path": str(item),
    #                 "type": "File",
    #                 "size": size_new,
    #             }
    #             list.append(node_file)
    #         size += size_new
    #     node_this["size"] = size
    #     return list,size


if __name__ == "__main__":
    # current_dir = Path.cwd()  # 获取当前工作目录
    current_dir = r"D:\test\fastapi"
    directory_tree = DirectoryTree.build_directory_list_root(current_dir)
    # 将目录树转换为 JSON 格式
    json_tree = json.dumps(
        directory_tree,
        # 默认输出ASCLL码，False可以输出中文。
        ensure_ascii=False,
        # 格式化
        indent=4,
    )
    print(json_tree)
