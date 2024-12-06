import sys
from tree_sitter import Language, Parser
import subprocess

from enum import Enum, auto
from pathlib import Path


# class syntax
class CodeType(Enum):
    python = "python"
    java = "java"
    cpp = "cpp"
    javascript = "javascript"
    rust = "rust"
    html = "html"
    markdown = "markdown"
    dart = "dart"
    c_sharp = "c-sharp"


def git_clone(repo: str, temp_dir: Path):
    try:
        print(f"Cloning {repo} into {temp_dir}")
        subprocess.run(["git","clone", repo], cwd=temp_dir, check=True)
        print(f"Successfully cloned {repo}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to clone repository {repo}: {e}")


class TreeSitterLangusges:
    path: Path

    def __init__(self, path: str):
        self.path = Path(path)
        if not self.path.exists():
            self.path.mkdir(parents=True)
        self.languages = {}

    def build(self, code_types: list[CodeType]):
        dll_names = "code"
        source_path_list = []
        failed_clones = []

        for code_type in code_types:
            code_type_name = code_type.value
            tree_sitter_code = f"tree-sitter-{code_type_name}"
            path_all = self.path / tree_sitter_code
            source_path_list.append(path_all)
            dll_names += f"-{code_type_name}"

            if not path_all.exists():
                # 使用绝对路径来确保克隆到正确的目录
                git_clone(
                    f"https://github.com/tree-sitter/{tree_sitter_code}.git", self.path
                )
                if not path_all.exists():  # 检查是否成功克隆
                    failed_clones.append(code_type_name)
                    source_path_list.remove(path_all)  # 移除未成功克隆的路径

        if failed_clones:
            print(f"The following repositories failed to clone: {failed_clones}")

        # 根据操作系统选择正确的扩展名
        ext = ".dll" if sys.platform.startswith("win") else ".so"
        dll_path = self.path / f"{dll_names}{ext}"

        if source_path_list:  # 如果有成功的克隆，则尝试构建库
            try:
                Language.build_library(
                    dll_path,
                    source_path_list,
                )
                print(f"Shared library built at {dll_path}")
            except Exception as e:
                print(f"Failed to build the shared library: {e}")
        else:
            print("No successful clones to build a shared library from.")

    def get_langusge(self, codeType: CodeType):
        return Language("test1/my-languages.dll", "dart")


# Language.build_library(
#   # so文件保存位置
#   'build/my-languages.dll',
#   # vendor文件下git clone的仓库
#   [
#     'tree-sitter-dart'
#   ]
# )


# 步骤 2: 加载编译后的 Dart 语言
# DART_LANGUAGE = Language("temp/my-languages.dll", "dart")


# class AstLanguages:
#     """ast分析代码"""

#     def __init__(self):
#         # Cache for parsers, keyed by language name
#         self.parsers = {}

#     def get_parser(self, text_type: CodeType):
#         if text_type not in self.parsers:
#             # Initialize parser and set the language
#             lang_module: object = TreeSitterLangusges.get(text_type)
#             if lang_module is None:
#                 raise ValueError(f"Unsupported language: {text_type}")
#             self.parsers[text_type] = Parser(Language(lang_module.language()))
#         return self.parsers[text_type]

#     def code2tree(self, text_type, text: str, encoding: str = "utf-8") -> Tree:
#         parser = self.get_parser(text_type)
#         # Parse the input text
#         tree: Tree = parser.parse(bytes(text, encoding))
#         return tree


if __name__ == "__main__":
    tree_sitter = TreeSitterLangusges("temp")
    tree_sitter.build([CodeType.cpp])
