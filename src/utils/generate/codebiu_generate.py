from pathlib import Path
from uuid import uuid4

from utils.code.file.file_io import FileIO
from utils.code.str.code_translate import snake_to_camel
from utils.generate.simple_template_engine import SimpleTemplateEngine
from utils.zip.zip_util import zip_full_path
from config.path import path_base
from config.index import files_path


# 使用模版位置
path_generate = path_base / "source" / "generate" / "codebiu"


class CodebiuGenerate:
    """代码生成器"""

    def create(data: dict):
        """生成所有代码"""
        # 基础对象名和驼峰
        name_snake = "test_generate"
        name_camel = snake_to_camel(name_snake)
        
        # 生成文件名
        file_name_snake= name_snake + ".py"
        
        # 生成代码文件夹 新资源地址和压缩
        BASE_PATH  = files_path/Path("Generate")/name_snake
        OUTPUT_DIR = uuid4().hex
        OUTPUT_ZIP = f"{OUTPUT_DIR}.zip"
        
        # 构建完整路径
        output_path = BASE_PATH / OUTPUT_DIR
        output_zip_path = BASE_PATH / OUTPUT_ZIP
        
        # 获取当前文件的路径
        current_file_path = Path(__file__).resolve()
        # 打开文件
        # controller
        path_controller_tmplate_in = path_generate / "controller.sh"
        template = FileIO.read(path_controller_tmplate_in, content)
        # 生成代码文件夹
        context = {"template_name": name_snake, "name_camel": name_camel}
        content = SimpleTemplateEngine.render(template, context)
        # 写入文件
        path_controller_out = files_path / "controller" / file_name_snake       
        FileIO.write(path_controller_out, content)
        # # 压缩
        zip_full_path(output_zip_path, [output_path])
        
    def create_domains(name_snake= "test_generate",do_db = [
            {"name": "key", "type": "str"},
            {"name": "value", "type": "str"},
        ]):
        """生成do"""
        
        
        return
    
    def create_all():
        pass
        


if __name__ == "__main__":
    CodebiuGenerate().create({"name": "test_generate"})
