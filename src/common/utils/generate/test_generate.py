from pathlib import Path

class TestGenerate:
    """测试文件生成器，用于根据源码路径自动创建对应的测试文件"""
    def __init__(self, from_dir="src", test_dir="tests"):
        """初始化测试生成器
        Args:
            from_dir (str): 源代码根目录，默认为'src'
            test_dir (str): 测试文件根目录，默认为'tests'
        """
        self.from_dir = from_dir
        self.test_dir = test_dir
        
    def _get_test_path(self, src_path):
        """将源码路径转换为测试文件路径
        Args:
            src_path (str|Path): 源代码文件路径
            
        Returns:
            Path: 生成的测试文件路径
            
        Raises:
            ValueError: 如果源码路径中不包含源代码根目录
        """
        src_path = Path(src_path).absolute()  # 转换为绝对路径
        parts = src_path.parts  # 获取路径各部分
        
        try:
            # 查找源代码根目录的位置
            src_index = parts.index(self.from_dir)
        except ValueError:
            raise ValueError(f"源码路径中不包含'{self.from_dir}'目录")
        
        # 用测试目录替换源码目录，重建路径
        test_path = Path(self.test_dir).joinpath(*parts[src_index+1:])
        # 在文件名前添加'test_'前缀
        return test_path.with_name(f"test_{test_path.name}")
    
    def create_file(self, src_path, db_fields_list=None):
        """创建测试文件
        Args:
            src_path (str|Path): 源代码文件路径
            db_fields_list (list, optional): 数据库字段列表（保留参数）
            
        Returns:
            Path: 创建的测试文件路径
        """
        # 获取测试文件路径
        test_path = self._get_test_path(src_path)
        
        # 确保父目录存在（不存在则创建）
        test_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入测试文件基本内容
        with test_path.open("w", encoding="utf-8") as f:
            f.write(f"# 测试文件：{src_path}\n")
            f.write("import pytest\n\n")
            f.write(f"from {self._get_import_path(src_path)} import *\n\n")
            f.write("# 在此添加测试用例\n")
        
        return test_path
    
    def _get_import_path(self, src_path):
        """获取源码文件的导入路径（模块路径）
        Args:
            src_path (str|Path): 源代码文件路径
            
        Returns:
            str: 可用于import语句的模块路径
        """
        src_path = Path(src_path).absolute()
        parts = src_path.parts
        
        try:
            # 查找源代码根目录的位置
            src_index = parts.index(self.from_dir)
        except ValueError:
            raise ValueError(f"源码路径中不包含'{self.from_dir}'目录")
        
        # 移除.py扩展名，并将路径转换为模块导入格式
        module_path = ".".join(parts[src_index:-1] + (src_path.stem,))
        return module_path
    
    def create_all(self, check_dir: str | Path) -> None:
        """遍历检查目录并创建缺失的测试文件
        
        Args:
            check_dir (str|Path): 要检查的目录路径
        """
        check_dir = Path(check_dir).absolute()
        
        # 确保检查目录在源码目录下
        if self.from_dir not in check_dir.parts:
            print(f"警告：检查目录{check_dir}不在{self.from_dir}下")
            return
            
        # 遍历目录下的所有.py文件
        for src_file in check_dir.rglob("*.py"):
            # 跳过__init__.py和测试文件
            if src_file.name.startswith("__") or src_file.name.startswith("test_"):
                continue
                
            # 获取对应的测试文件路径
            try:
                test_path = self._get_test_path(src_file)
                if not test_path.exists():
                    print(f"创建测试文件: {test_path}")
                    self.create_file(src_file)
            except ValueError as e:
                print(f"跳过文件{src_file}: {e}")
    
if __name__ == "__main__":
    # 创建测试生成器实例
    generator = TestGenerate()

    # 为指定源码文件生成测试文件
    test_file = generator.create_all(r"D:\a0_wx\codebiu\server-example\src\common\utils\dataBase")
    # test_file = generator.create_file(r"D:\github\codebiu\server-example\src\common\utils\file\dir_manager.py")

    # 输出生成的测试文件路径
    # print(f"已创建测试文件：{test_file}")