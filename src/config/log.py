import logging
import logging.config
from pathlib import Path

# 默认的warning级别，只输出warning以上的
# 使用basicConfig()来指定日志级别和相关信息
from config.path import dir_log
from config.index import conf
from utils.enum.color import Color
from utils.log.ColoredConsoleHandler import ColoredConsoleHandler
from utils.log.CustomTimedRotatingFileHandler import CustomTimedRotatingFileHandler

"""
    生成文件log和带颜色控制台log
"""
is_dev: bool = conf["state"]["is_dev"]
def setup_logging():
    # 获取根日志记录器
    logger = logging.getLogger()
    # 如果已经存在处理器，则不再重新配置
    if logger.handlers:
        return
    logger.propagate = False
    logger.setLevel(logging.DEBUG)
    # 格式
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # 控制台log
    console_handler = ColoredConsoleHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)
    if is_dev:
        logger.addHandler(console_handler)


    # 文件log
    def external_custom_function():
        """每日log额外处理"""
        logger.info("...new log")


    # 文件log路径 替换%Y-%m-%d
    files_path_log_error = Path(dir_log) / "error_%Y-%m-%d.log"

    file_handler = CustomTimedRotatingFileHandler(
        files_path_log_error,
        # 日志切割时间
        when="midnight",
        interval=1,
        # 保留天数
        backupCount=14,
        # 自定义切换调用函数
        custom_function=external_custom_function,
    )
    file_handler.setFormatter(formatter)
    if is_dev:
        file_handler.setLevel(logging.INFO)
    else:
        file_handler.setLevel(logging.ERROR)
    logger.addHandler(file_handler)
    
setup_logging()
logger = logging.getLogger()
# 输出带颜色的日志
logger.info('%s %s', 'ok...log配置', "多log")
