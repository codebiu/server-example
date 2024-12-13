import sys, pathlib

[sys.path.append(str(pathlib.Path(__file__).resolve().parents[i])) for i in range(4)]
import pytest
from enum import Enum, auto
from tree_sitter import Tree, Parser
from src.utils.enum.code import CodeType
# from src.utils.ast.ast_languages import AstLanguages


# 假设这里包含了你的 AstLanguages 类的实现。
# from your_module import AstLanguages, LANGUAGE_MAP, CodeType


@pytest.fixture
def ast_languages_instance() -> AstLanguages:
    """提供一个 AstLanguages 类的实例"""
    return AstLanguages()


def test_get_parser(ast_languages_instance:AstLanguages):
    """测试 get_parser 方法是否正确返回 Parser 对象"""
    for code_type in CodeType:
        parser = ast_languages_instance.get_parser(code_type)
        assert isinstance(parser, Parser), f"Failed to get parser for {code_type.name}"


def test_code2tree(ast_languages_instance:AstLanguages):
    """测试 code2tree 方法是否能够解析不同类型的代码字符串"""
    test_cases = {
        CodeType.python: "print('Hello, world!')",
        CodeType.java: 'public class HelloWorld { public static void main(String[] args) { System.out.println("Hello, world!"); } }',
        CodeType.javascript: "console.log('Hello, world!');",
        CodeType.html: "<html><body><h1>Hello, world!</h1></body></html>",
        # markdown
        CodeType.markdown: "# Hello, world!  \n\nThis is a test.",
    }

    for code_type, code_string in test_cases.items():
        tree = ast_languages_instance.code2tree(code_type, code_string)
        assert isinstance(tree, Tree), f"Failed to parse code for {code_type.name}"
        # 这里还可以添加更多的断言来检查语法树的具体结构或节点类型等。


def test_unsupported_language(ast_languages_instance:AstLanguages):
    """测试对于不支持的语言，应该抛出 ValueError 异常"""
    with pytest.raises(ValueError):
        ast_languages_instance.get_parser(CodeType("unsupported"))
