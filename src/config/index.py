# self
import sys
from pathlib import Path
# lib
import yaml

from common.utils.config.config_manager_yaml import ConfigManagerYaml

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
print("path_base目录根路径", path_base)

# config path 配置路径
config_yaml = path_base / "config.yaml"
# 配置dict
conf = ConfigManagerYaml(config_yaml)

# 配置文件内修改配置文件路径
conf_use = conf["state.config_path"]
if conf_use is not None:
    config_yaml = path_base / conf_use
    # 判断有没有
    if config_yaml.exists():
        conf = ConfigManagerYaml(config_yaml)
        
