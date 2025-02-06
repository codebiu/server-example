from pathlib import Path
from uuid import uuid4

from utils.code.file.file_io import FileIO
from utils.code.str.code_translate import snake_to_camel
from utils.generate.simple_template_engine import SimpleTemplateEngine
from utils.zip.zip_util import zip_full_path
from config.path import files_path_generate, project_path_base


# 使用模版位置
path_generate = project_path_base / "source" / "generate" / "codebiu"


class CodebiuGenerate:
    """代码生成器"""

    def __init__(self, name_snake):
        self.name_snake = name_snake
        # 生成代码文件夹 新资源地址和压缩
        self.BASE_PATH = Path(files_path_generate) / name_snake
        self.OUTPUT_DIR = uuid4().hex
        self.OUTPUT_ZIP = f"{self.OUTPUT_DIR}.zip"

        # 构建完整路径
        self.output_path = self.BASE_PATH / self.OUTPUT_DIR
        self.output_zip_path = self.BASE_PATH / self.OUTPUT_ZIP

    def create_domain(
        self,
        do_db=[
            {"name": "key", "type": "str"},
            {"name": "value", "type": "str"},
        ],
    ):
        """生成do"""
        return

    def create(self, dir_name="controller"):
        """生成do"""
        name_camel = snake_to_camel(self.name_snake)
        # 打开文件
        # controller
        file_name_temolate = dir_name + ".sh"
        path_controller_tmplate_in = path_generate / file_name_temolate
        template = FileIO.read(path_controller_tmplate_in)
        # 生成代码文件夹
        context = {"template": self.name_snake, "Template": name_camel}
        content = SimpleTemplateEngine.render(template, context)
        # 写入文件
        file_name_snake = self.name_snake + ".py"
        path_controller_out = self.output_path / dir_name / file_name_snake
        FileIO.write(path_controller_out, content)

    def create_all(self):
        self.create("controller")
        # # 压缩
        zip_full_path(self.output_zip_path, [self.output_path])


if __name__ == "__main__":
    codebiuGenerate = CodebiuGenerate("test_generate_this")
    codebiuGenerate.create_all()
