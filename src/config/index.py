# self
from config.path import path_base
# lib
import yaml

# config path 配置路径
config_yaml = path_base / "config.yaml"
# 配置dict
conf = yaml.safe_load(config_yaml.read_text(encoding="utf-8"))

# 配置文件内修改配置文件路径
conf_new = conf["state"]["config_path"]
if conf_new is not None:
    config_yaml = path_base / conf_new
    conf = yaml.safe_load(config_yaml.read_text(encoding="utf-8"))