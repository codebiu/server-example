
import tree_sitter_python as tspython
import tree_sitter_java as tsjava
import tree_sitter_javascript as tsjs
import tree_sitter_html as tshtml
import tree_sitter_markdown as tsmd
from tree_sitter import Language, Parser,Tree

from ..enum.code import CodeType

# Define a mapping from language names to their respective Tree-sitter Language objects
LANGUAGE_MAP = {
    CodeType.python: tspython,
    CodeType.java: tsjava,
    CodeType.javascript: tsjs,
    CodeType.html: tshtml,
    CodeType.markdown: tsmd,
}

class AstLanguages:
    """ast分析代码"""
    
    def __init__(self):
        # Cache for parsers, keyed by language name
        self.parsers = {}

    def get_parser(self, text_type:CodeType):
        if text_type not in self.parsers:
            # Initialize parser and set the language
            lang_module:object = LANGUAGE_MAP.get(text_type)
            if lang_module is None:
                raise ValueError(f"Unsupported language: {text_type}")
            self.parsers[text_type] = Parser(Language(lang_module.language()))
        return self.parsers[text_type]

    def code2tree(self, text_type, text: str, encoding: str = "utf-8") -> Tree:
        parser = self.get_parser(text_type)
        # Parse the input text
        tree:Tree = parser.parse(bytes(text, encoding))
        return tree
    
    def  chunk(self, tree:Tree,text, encoding: str = "utf-8") -> dict:
        # Start processing the tree from the root node
        code_tree = {"import": [], "class": [], "function": [], "other": []}
        self.process_node(code_tree, tree.root_node, bytes(text, encoding))
        
        # Here you would normally return a processed result.
        # For demonstration purposes, we will simply return the code_tree.
        return code_tree

    def process_node(self, code_tree, node, text_bytes):
        # This method should be implemented to recursively process the AST nodes.
        # It can use similar logic to your original chunk_node function.
        pass  # Placeholder for actual implementation




if __name__ == "__main__":
    import time
    
    # 创建分割器
    chunker = AstLanguages()
    start_time = time.time()

    # 读取python文件到字符串
    # with open(r"D:\test\fastapi\routing.py", "r", encoding="utf-8") as f:
    with open(r"test-data\text\test.java", "r", encoding="utf-8") as f:
        text_str = f.read()
        print(time.time() - start_time)
        start_time = time.time()
        new_chunks = chunker.chunk(CodeType.java,text_str)
        # print(new_chunks)
        print(time.time() - start_time)
        start_time = time.time()
