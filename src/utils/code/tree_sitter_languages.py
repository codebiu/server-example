import sys
from tree_sitter import Language, Parser, Tree
from pathlib import Path
# self
from utils.common.git_utils import git_clone
from utils.enum.code import CodeType


class TreeSitterlanguages:
    path: Path

    def __init__(self, path_build: str = 'tree_sitter_build', path_source: str = 'tree-sitter-sources'):
        self.path_source = Path(path_source)
        self.path_build = Path(path_build)
        if not self.path_source.exists():
            self.path_source.mkdir(parents=True)
        # Cache for parsers, keyed by language name
        self.parsers = {}

    def build(self, code_types: list[CodeType]):
        failed_clones = []
        for code_type in code_types:
            tree_sitter_code = f"tree-sitter-{code_type.value}"
            code_source_path = self.path_source / tree_sitter_code
            dll_build_path = self.get_dll_build_path(code_type)
            if not code_source_path.exists():
                # 使用绝对路径来确保克隆到正确的目录
                git_clone(
                    f"https://github.com/tree-sitter/{tree_sitter_code}.git", self.path_source
                )
                if not code_source_path.exists():  # 检查是否成功克隆
                    failed_clones.append(code_type.value)
                    try:
                        Language.build_library(
                            dll_build_path,
                            [code_source_path],
                        )
                        print(f"Shared library built at {dll_build_path}")
                    except Exception as e:
                        print(f"Failed to build the shared library: {e}")
                else:
                    print(f"Successfully cloned {tree_sitter_code}")
        if failed_clones:
            print(f"The following repositories failed to clone: {failed_clones}")



    def get_dll_build_path(self, code_type: CodeType)-> str:
        code_type_name = code_type.value
        dll_name = f"tree-sitter-{code_type_name}"
         # 根据操作系统选择正确的扩展名
        ext = ".dll" if sys.platform.startswith("win") else ".so"
        dll_build_path = str(self.path_build / f"{dll_name}{ext}")
        return dll_build_path
    
    
    def get_language(self, code_type: CodeType):
        dll_build_path = self.get_dll_build_path(code_type)
        return Language(dll_build_path, code_type.value)
    
    def get_parser(self, code_type:CodeType):
        if code_type not in self.parsers:
            # Initialize parser and set the language
            lang_module:Language = self.get_language(code_type)
            if lang_module is None:
                raise ValueError(f"Unsupported language: {code_type}")
            self.parsers[code_type] = Parser(lang_module)
        return self.parsers[code_type]

    def code2tree(self, code_type, text: str, encoding: str = "utf-8") -> Tree:
        parser = self.get_parser(code_type)
        # Parse the input text
        tree:Tree = parser.parse(bytes(text, encoding))
        return tree


if __name__ == "__main__":
    import time
    tree_sitter = TreeSitterlanguages("temp")
    tree_sitter.build([CodeType.dart])   

    # 读取python文件到字符串
    # with open(r"D:\test\fastapi\routing.py", "r", encoding="utf-8") as f:
    with open(r"test-data\text\test.java", "r", encoding="utf-8") as f:
        text_str = f.read()
        start_time = time.time()
        new_chunks = tree_sitter.code2tree(CodeType.java,text_str)
        print(time.time() - start_time)
