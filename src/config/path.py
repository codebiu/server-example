# 获取当前脚本文件的绝对路径
from pathlib import Path
from config.index import conf, path_base

project_path_base = path_base
# 基础文件路径
files_path_dict = conf["files_path"]
dir_uploaded: Path = Path(files_path_dict["uploaded"])
dir_log: Path = Path(files_path_dict["log"])
dir_generate: Path = Path(files_path_dict["generate"])
dir_temp: Path = Path(files_path_dict["temp"])
dir_test: Path = Path(files_path_dict["test"])


# 默认服务启动就创建创建
try:
    dir_uploaded.mkdir(parents=True, exist_ok=True)
    dir_log.mkdir(parents=True, exist_ok=True)
    dir_generate.mkdir(parents=True, exist_ok=True)
    dir_temp.mkdir(parents=True, exist_ok=True)
    dir_test.mkdir(parents=True, exist_ok=True)
except Exception as e:
    print("创建默认目录失败", e)
