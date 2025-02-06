# 获取当前脚本文件的绝对路径
from pathlib import Path
from config.index import conf,path_base

project_path_base = path_base
# 基础文件路径
files_path = conf["files_path"]
files_path_uploaded:str = files_path['uploaded']
files_path_log:str = files_path['log']
files_path_generate:str = files_path['generate']
files_path_temp:str = files_path['temp']


# 没有就创建
Path(files_path_uploaded).mkdir(parents=True, exist_ok=True)
Path(files_path_log).mkdir(parents=True, exist_ok=True)
Path(files_path_generate).mkdir(parents=True, exist_ok=True)
Path(files_path_temp).mkdir(parents=True, exist_ok=True)
