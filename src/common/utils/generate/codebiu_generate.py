from pathlib import Path
from uuid import uuid4
import zipfile
import io

from common.utils.code.file.file_io import FileIO
from common.utils.code.str.code_translate import (
    snake_to_camel_first_lower,
    snake_to_camel_first_capital,
)
from common.utils.generate.simple_template_engine import (
    SimpleTemplateEngine,
    SimpleTemplateEngineFull,
)
from config.path import dir_generate, project_path_base


# 使用模版位置
path_generate = project_path_base / "source" / "generate" / "codebiu"


class CodebiuGenerate:
    """代码生成器

    用于根据模板生成代码文件，并可以选择将生成的文件保存到磁盘或返回压缩包内容。
    """

    def __init__(
        self,
        save_to_disk=False,
    ):
        """初始化代码生成器

        Args:
            save_to_disk (bool, optional): 是否将生成的文件保存到磁盘。默认为False。
        """
        self.save_to_disk = save_to_disk

    def create(
        self,
        name_snake,
        db_fields_list=[
            {"name": "key", "type": "str"},
            {"name": "value", "type": "str"},
        ],
    ):
        """创建代码文件

        Args:
            name_snake (str): 蛇形命名的模块名称，例如 "generate_table1"。
            db_fields_list (list, optional): 数据库字段列表，每个字段包含名称和类型。默认为 [{"name": "key", "type": "str"}, {"name": "value", "type": "str"}]。

        Returns:
            io.BytesIO: 包含生成代码文件的压缩包内容。
        """
        self.name_snake = name_snake
        self.name_camel_first_lower = snake_to_camel_first_lower(self.name_snake)
        self.name_camel_first_capital = snake_to_camel_first_capital(self.name_snake)
        # 获取上下文
        context = self.get_context()
        context_domain = self.get_context_domain(db_fields_list)

        # 在内存中生成文件内容
        files = [
            self.create_in_memory("controller", context),
            self.create_in_memory("service", context),
            self.create_in_memory("dao", context),
            self.create_in_memory("do", context_domain),
        ]

        # 在内存中创建压缩包
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for dir_name, file_name, file_content in files:
                # 将文件内容写入压缩包
                zip_file.writestr(f"{dir_name}/{file_name}", file_content.getvalue())

        # 根据参数决定是否保存到本地
        if self.save_to_disk:
            output_zip_path = (
                Path(dir_generate) / f"{self.name_snake}_{uuid4().hex}.zip"
            )
            output_zip_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_zip_path, "wb") as f:
                f.write(zip_buffer.getvalue())
            print(f"压缩包已保存到本地: {output_zip_path}")

        # 返回压缩包内容
        zip_buffer.seek(0)  # 将指针移动到文件开头
        return zip_buffer

    def create_in_memory(self, dir_name, context):
        """在内存中生成文件内容

        Args:
            dir_name (str): 目录名称，例如 "controller"。
            context (dict): 模板上下文数据。

        Returns:
            tuple: 包含目录名称、文件名称和文件内容的元组。
        """
        file_name_template = dir_name + ".sh"
        path_controller_template_in = path_generate / file_name_template
        template = FileIO.read(path_controller_template_in)

        # 渲染模板
        content = SimpleTemplateEngineFull.render(template, context)
        # 在内存中创建文件内容
        file_name_snake = self.name_snake + ".py"
        file_content = io.StringIO(content)
        return dir_name, file_name_snake, file_content

    def get_context(self):
        """获取模板上下文

        Returns:
            dict: 包含模板名称、驼峰命名（首字母小写）和驼峰命名（首字母大写）的上下文数据。
        """
        context = {
            "template_name": self.name_snake,
            "templateName": self.name_camel_first_lower,
            "TemplateName": self.name_camel_first_capital,
        }
        return context

    def get_context_domain(self, db_fields_list):
        """获取带数据库字段的模板上下文

        Args:
            db_fields_list (list): 数据库字段列表，每个字段包含名称和类型。

        Returns:
            dict: 包含模板名称、驼峰命名（首字母小写）、驼峰命名（首字母大写）和数据库字段的上下文数据。
        """
        db_fields_str = ""
        for db_field in db_fields_list:
            db_field_name = db_field.get("name")
            db_field_type = db_field.get("type")
            db_field_description = db_field.get(
                "description", ""
            )  # 如果没有描述，默认为空字符串
            db_fields_str += f'    {db_field_name}: {db_field_type} = Field(description="{db_field_description}")\n'

        context = {
            "template_name": self.name_snake,
            "templateName": self.name_camel_first_lower,
            "TemplateName": self.name_camel_first_capital,
            "DBFields": db_fields_str,
        }
        return context


if __name__ == "__main__":
    # 示例: 创建代码生成器并生成代码文件
    codebiuGenerate = CodebiuGenerate(True)

    # 示例 1: 直接返回压缩包内容 或 保存到本地
    zip_buffer = codebiuGenerate.create(
        "article",
        db_fields_list=[
            {"name": "id", "type": "int", "description": "文章的唯一标识符"},
            {"name": "title", "type": "str", "description": "文章的标题"},
            {"name": "content", "type": "str", "description": "文章的内容"},
            {"name": "author_id", "type": "int", "description": "作者的用户ID"},
            {"name": "category", "type": "str", "description": "文章的分类"},
            {
                "name": "tags",
                "type": "list[str]",
                "description": "文章的标签（列表形式）",
            },
            {"name": "created_at", "type": "datetime", "description": "文章的创建时间"},
            {
                "name": "updated_at",
                "type": "datetime",
                "description": "文章的最后更新时间",
            },
            {"name": "is_published", "type": "bool", "description": "文章是否已发布"},
            {"name": "views", "type": "int", "description": "文章的浏览量"},
            {
                "name": "slug",
                "type": "str",
                "description": "文章的URL友好标识（用于SEO）",
            },
        ],
    )
    #  src\module_blog
