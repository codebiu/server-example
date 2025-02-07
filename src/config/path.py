# 获取当前脚本文件的绝对路径
from pathlib import Path
from config.index import conf,path_base

project_path_base = path_base
# 基础文件路径
files_path_dict = conf["files_path"]
dir_uploaded:str = files_path_dict['uploaded']
dir_log:str = files_path_dict['log']
dir_generate:str = files_path_dict['generate']
dir_temp:str = files_path_dict['temp']


# 没有就创建
Path(dir_uploaded).mkdir(parents=True, exist_ok=True)
Path(dir_log).mkdir(parents=True, exist_ok=True)
Path(dir_generate).mkdir(parents=True, exist_ok=True)
Path(dir_temp).mkdir(parents=True, exist_ok=True)
