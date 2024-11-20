# self
from config.path import config_yaml

# lib
import yaml
# from pathlib import Path

# 配置dict
conf = yaml.safe_load(config_yaml.read_text(encoding="utf-8"))
