from tree_sitter import Language,Parser

# Language.build_library(
#   # so文件保存位置
#   'build/my-languages.dll',
#   # vendor文件下git clone的仓库
#   [
#     'tree-sitter-dart'
#   ]
# )



# 步骤 2: 加载编译后的 Dart 语言
DART_LANGUAGE = Language('test1/my-languages.dll', 'dart')

# 步骤 3: 初始化解析器
parser = Parser()
parser.set_language(DART_LANGUAGE)

# 步骤 4: 解析 Dart 代码
dart_code = """
void main() {
    print('Hello, World!');
}
"""
tree = parser.parse(bytes(dart_code, "utf8"))

# 步骤 5: 遍历语法树
def print_node(node, code, depth=0):
    print(f"{'  ' * depth}{node.type}: {code[node.start_byte:node.end_byte].decode('utf-8')}")
    for child in node.children:
        print_node(child, code, depth + 1)

print_node(tree.root_node, bytes(dart_code, "utf8"))https://github.com/tree-sitter/tree-sitter-cpp.git