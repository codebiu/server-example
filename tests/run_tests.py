import pytest

if __name__ == "__main__":
    # 运行所有测试
    # pytest.main(['-v'])  # -v 表示详细模式
    
    # 或者运行特定的测试文件
    # utils
    pytest.main([r'tests\utils\ast\test_ast_languages.py'])
    
    # 或者运行特定的测试函数
    # pytest.main(['tests/test_module1.py::test_add'])
