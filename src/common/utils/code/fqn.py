import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Node

parser =Parser(Language(tspython.language()))

# TODO 全变量名
def get_fqn(node, scope=[]):
    if node.type == 'function_definition' or node.type == 'class_definition':
        name_node = next(n for n in node.children if n.type == 'identifier')
        fqn = '.'.join(scope + [name_node.text.decode()])
        print(fqn)  # 或者保存到列表中
        
        # 如果是类定义，则更新作用域
        new_scope = scope + [name_node.text.decode()] if node.type == 'class_definition' else scope
        for child in node.children:
            get_fqn(child, new_scope)
    else:
        for child in node.children:
            get_fqn(child, scope)

code = b"""
import foo.bar
class MyClass:
    def my_method(self):
        pass
"""

tree = parser.parse(code)
get_fqn(tree.root_node)