from pathlib import Path
import aiofiles
import asyncio


class AsyncTestGenerate:
    """异步测试文件生成器，用于根据源码路径自动创建对应的测试文件"""

    def __init__(self, from_dir="src", test_dir="tests"):
        """初始化测试生成器
        Args:
            from_dir (str): 源代码根目录，默认为'src'
            test_dir (str): 测试文件根目录，默认为'tests'
        """
        self.from_dir = from_dir
        self.test_dir = test_dir

    async def _get_test_path(self, src_path):
        """将源码路径转换为测试文件路径
        Args:
            src_path (Path): 源代码文件路径

        Returns:
            Path: 生成的测试文件路径

        Raises:
            ValueError: 如果源码路径中不包含源代码根目录
        """
        src_path = src_path.absolute()
        parts = src_path.parts

        try:
            src_index = parts.index(self.from_dir)
        except ValueError:
            raise ValueError(f"源码路径中不包含'{self.from_dir}'目录")

        test_path = Path(self.test_dir).joinpath(*parts[src_index + 1 :])
        return test_path.with_name(f"test_{test_path.name}")

    async def create_file(self, src_path):
        """异步创建测试文件
        Args:
            src_path (Path): 源代码文件路径

        Returns:
            Path: 创建的测试文件路径
        """
        # 获取测试文件路径
        test_path = await self._get_test_path(src_path)

        # 确保父目录存在（不存在则创建）
        test_path.parent.mkdir(parents=True, exist_ok=True)

        # 写入测试文件内容
        content = f"""# 测试文件：{src_path}
import pytest

from {await self._get_import_path(src_path)} import *

# 在此添加测试用例
"""
        async with aiofiles.open(test_path, "w", encoding="utf-8") as f:
            await f.write(content)

        return test_path

    async def _get_import_path(self, src_path):
        """获取源码文件的导入路径（模块路径）
        Args:
            src_path (Path): 源代码文件路径

        Returns:
            str: 可用于import语句的模块路径
        """
        src_path = src_path.absolute()
        parts = src_path.parts

        try:
            src_index = parts.index(self.from_dir)
        except ValueError:
            raise ValueError(f"源码路径中不包含'{self.from_dir}'目录")

        module_path = ".".join(parts[src_index:-1] + (src_path.stem,))
         # 如果模块路径以 'src.' 开头，则去除 'src.' 前缀
        if module_path.startswith(f"{self.from_dir}."):
            module_path = module_path[len(f"{self.from_dir}."):]
        return module_path

    async def _process_file(self, src_file):
        """处理单个文件"""
        try:
            test_path = await self._get_test_path(src_file)
            if not test_path.exists():
                print(f"创建测试文件: {test_path}")
                await self.create_file(src_file)
        except ValueError as e:
            print(f"跳过文件{src_file}: {str(e)}")

    async def create_all(self, check_dir):
        """异步遍历检查目录并创建缺失的测试文件

        Args:
            check_dir (Path): 要检查的目录路径
        """
        check_dir = Path(check_dir).absolute()

        # 确保检查目录在源码目录下
        if self.from_dir not in check_dir.parts:
            print(f"警告：检查目录{check_dir}不在{self.from_dir}下")
            return

        # 收集所有.py文件
        all_files = []
        for src_file in check_dir.rglob("*.py"):
            if not src_file.name.startswith("__") and not src_file.name.startswith(
                "test_"
            ):
                all_files.append(src_file)

        # 异步处理所有文件
        tasks = [self._process_file(f) for f in all_files]
        await asyncio.gather(*tasks)

    @staticmethod
    def run(check_dir, from_dir="src", test_dir="tests"):
        """同步运行异步方法"""
        generator = AsyncTestGenerate(from_dir, test_dir)
        asyncio.run(generator.create_all(check_dir))


if __name__ == "__main__":
    # 同步方式运行
    AsyncTestGenerate.run(
        r"D:\github\codebiu\server-example\src\common\utils\ai\framework"
    )

    # 或者异步方式运行（在async函数中）
    # async def main():
    #     generator = AsyncTestGenerate()
    #     await generator.create_all(r"D:\github\codebiu\server-example\src\common\utils\ai\framework")
    #
    # asyncio.run(main())
