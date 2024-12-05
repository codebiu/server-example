from typing import Dict, Optional, List, Tuple
import ast

# 假设符号表是一个字典，键是全限定名（FQN），值是定义的位置和其他元数据
symbol_table: Dict[str, dict] = {}
# 导入模块映射，键是导入语句中的别名或模块名，值是实际的模块名
imports_mapping: Dict[str, str] = {}

def resolve_fqn(identifier: str, current_scope: str) -> Optional[str]:
    """
    尝试解析给定标识符的全限定名称。
    :param identifier: 要解析的标识符名称。
    :param current_scope: 当前作用域字符串表示。
    :return: 如果找到则返回全限定名；否则返回None。
    """
    fqn = None
    # 尝试在当前作用域内查找
    if symbol_table.get(f"{current_scope}.{identifier}"):
        fqn = f"{current_scope}.{identifier}"
    else:
        # 如果不在当前作用域，则尝试上一级作用域，直到全局作用域
        parent_scope = get_parent_scope(current_scope)
        while parent_scope and not fqn:
            if symbol_table.get(f"{parent_scope}.{identifier}"):
                fqn = f"{parent_scope}.{identifier}"
            parent_scope = get_parent_scope(parent_scope)

        # 如果仍然找不到，可能是来自导入的模块
        if not fqn:
            fqn = resolve_imported_identifier(identifier)

    return fqn


def resolve_imported_identifier(identifier: str) -> Optional[str]:
    """
    解析导入模块中的标识符。
    :param identifier: 标识符名称。
    :return: 如果找到则返回全限定名；否则返回None。
    """
    for alias, module_name in imports_mapping.items():
        # 检查是否为直接导入的标识符（如 from module import identifier）
        if f"{module_name}.{identifier}" in symbol_table:
            return f"{module_name}.{identifier}"

        # 检查是否为通过别名导入的标识符（如 import module as alias 或 from module import identifier as alias）
        if alias == identifier and module_name in symbol_table:
            return module_name

    return None


def get_parent_scope(scope: str) -> Optional[str]:
    """
    返回给定作用域的父级作用域。
    :param scope: 作用域字符串表示。
    :return: 父级作用域字符串表示；如果已经是全局作用域，则返回None。
    """
    parts = scope.split('.')
    if len(parts) <= 1:
        return None  # 已经是最外层作用域
    return '.'.join(parts[:-1])


def build_symbol_table(node: ast.AST, scope: str = '') -> None:
    """
    遍历AST并填充符号表。
    :param node: 当前节点。
    :param scope: 当前作用域。
    """
    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
        symbol_table[f"{scope}.{node.name}"] = {
            'type': type(node).__name__,
            'location': (node.lineno, node.col_offset),
            # 可以添加更多属性...
        }
        new_scope = f"{scope}.{node.name}" if scope else node.name
        for child in ast.iter_child_nodes(node):
            build_symbol_table(child, new_scope)
    elif isinstance(node, ast.ImportFrom):
        for alias in node.names:
            imported_name = f"{node.module}.{alias.name}" if node.module else alias.name
            asname = alias.asname or alias.name
            imports_mapping[asname] = imported_name
    elif isinstance(node, ast.Import):
        for alias in node.names:
            imports_mapping[alias.asname or alias.name] = alias.name

    for child in ast.iter_child_nodes(node):
        build_symbol_table(child, scope)


# 示例：解析一个Python文件并构建符号表
if __name__ == "__main__":
    with open('example.py', 'r') as file:
        source_code = file.read()
    
    tree = ast.parse(source_code)
    build_symbol_table(tree)

    # 测试解析某个标识符的FQN
    print(resolve_fqn('some_function', 'example'))