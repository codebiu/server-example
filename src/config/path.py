# 获取当前脚本文件的绝对路径
import sys
from pathlib import Path


# 获取当前脚本文件的绝对路径
def app_path() -> Path:
    if hasattr(sys, "frozen"):  # Python解释器的完整路径
        # build环境 pyinstaller打包后的exe目录
        path_base = Path(sys.executable).parent  # 使用pyinstaller打包后的exe目录
    else:
        # dev环境
        current_script_path = Path(__file__).resolve()
        # 获取当前脚本所在目录的父目录的父目录的路径
        path_base = current_script_path.parent.parent.parent
    return path_base


# 目录根路径
path_base = app_path()
print("path_base", path_base)
