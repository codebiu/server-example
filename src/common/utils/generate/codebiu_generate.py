from pathlib import Path
from uuid import uuid4

from common.utils.code.file.file_io import FileIO
from common.utils.code.str.code_translate import (
    snake_to_camel_first_lower,
    snake_to_camel_first_capital,
)
from common.utils.generate.simple_template_engine import (
    SimpleTemplateEngine,
    SimpleTemplateEngineFull,
)
from common.utils.zip.zip_util import zip_full_path
from config.path import dir_generate, project_path_base


# 使用模版位置
path_generate = project_path_base / "source" / "generate" / "codebiu"


class CodebiuGenerate:
    """代码生成器"""

    def __init__(self, name_snake):
        self.name_snake = name_snake
        self.name_camel_first_lower = snake_to_camel_first_lower(self.name_snake)
        self.name_camel_first_capital = snake_to_camel_first_capital(self.name_snake)
        # 生成代码文件夹 新资源地址和压缩
        self.BASE_PATH = Path(dir_generate) / name_snake
        self.OUTPUT_DIR = uuid4().hex
        self.OUTPUT_ZIP = f"{self.OUTPUT_DIR}.zip"

        # 构建完整路径
        self.output_path = self.BASE_PATH / self.OUTPUT_DIR
        self.output_zip_path = self.BASE_PATH / self.OUTPUT_ZIP

    def create(self, dir_name, context):
        """生成do"""
        file_name_temolate = dir_name + ".sh"
        path_controller_tmplate_in = path_generate / file_name_temolate
        template = FileIO.read(path_controller_tmplate_in)
       
        # content = SimpleTemplateEngine.render(template, context)
        content = SimpleTemplateEngineFull.render(template, context)
        # 写入文件
        file_name_snake = self.name_snake + ".py"
        path_controller_out = self.output_path / dir_name / file_name_snake
        FileIO.write(path_controller_out, content)
    def get_context(self):
        """生成do"""
        context = {
            "template_name": self.name_snake,
            "templateName": self.name_camel_first_lower,
            "TemplateName": self.name_camel_first_capital,
        }
        return context
    def get_context_domain(
        self,
        db_fields_list=[
            {"name": "key", "type": "str"},
            {"name": "value", "type": "str"},
        ],
    ):
        """生成do"""
        db_fields_str = ""
        for db_field in db_fields_list:
            db_field_name = db_field.get("name")
            db_field_type = db_field.get("type")
            db_fields_str += f"    {db_field_name}: {db_field_type}\n"

        context = {
            "template_name": self.name_snake,
            "templateName": self.name_camel_first_lower,
            "TemplateName": self.name_camel_first_capital,
            "DBFields": db_fields_str,
        }
        return context

    def create_all(self):
         # 生成代码文件夹
        context = self.get_context()
        self.create("controller",context)
        self.create("service",context)
        self.create("dao",context)
        # domain
        db_fields_list = [
            {"name": "key", "type": "str"},
            {"name": "value", "type": "str"},
        ]
        context_domain = self.get_context_domain(db_fields_list)
        self.create("do",context_domain)
        # # 压缩
        zip_full_path(self.output_zip_path, [self.output_path])


if __name__ == "__main__":
    codebiuGenerate = CodebiuGenerate("generate_table")
    codebiuGenerate.create_all()
