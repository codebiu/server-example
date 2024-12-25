from pathlib import Path

from utils.generate.simple_template_engine import SimpleTemplateEngine
from utils.zip.zip_util import zip_full_path


class CodebiuGenerate:
    """代码生成器"""

    def create(data: dict):
        """生成代码"""
        path_out_base = Path("todo")
        # 基础对象名和驼峰
        name_snake = "test_generate"
        name_camel = CodebiuGenerate.snake_to_camel(name_snake)
        
        # 生成代码文件夹
        path_out = path_out_base / name_snake

        #
        # 获取当前文件的路径
        current_file_path = Path(__file__).resolve()
        # 打开文件
        # controller
        file_path_controller = current_file_path.parent / "template" / "controller.py.template"
        CodebiuGenerate.create_this(
            file_path_controller,
            current_file_path.parent / "template" / "test_generate.py.template",
            {"name_snake": name_snake, "name_camel": name_camel},
        )
        # 压缩
        zip_full_path("test_generate.zip", [path_out])

    def create_this(out_file_path: str, template, context):
        """写入代码"""
        content = SimpleTemplateEngine.render(template, context)
        # 写入文件 没有就创建
        Path(out_file_path).parent.mkdir(parents=True, exist_ok=True)
        # 写入文件
        with open(out_file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def snake_to_camel(snake_str):
        # 分割字符串，转换成驼峰
        components = snake_str.split("_")
        # 将第一个单词保持小写，后面的单词首字母大写
        return components[0] + "".join(x.title() for x in components[1:])


if __name__ == "__main__":
    CodebiuGenerate().create({"name": "test_generate"})
