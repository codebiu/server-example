import logging
import logging.config
from pathlib import Path

# 默认的warning级别，只输出warning以上的
# 使用basicConfig()来指定日志级别和相关信息
from config.path import dir_log
from config.index import conf
from common.utils.log.ColoredConsoleHandler import ColoredConsoleHandler
from common.utils.log.CustomTimedRotatingFileHandler import (
    CustomTimedRotatingFileHandler,
)

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
    # 开发状态下，输出控制台log
    if is_dev:
        logger.addHandler(console_handler)

    # 文件log
    def external_custom_function():
        """每日log额外处理"""
        logger.info("...new log")

    # 文件log路径 替换%Y-%m-%d
    files_path_log_info = dir_log / "info_%Y-%m-%d.log"
    files_path_log_error = dir_log / "error_%Y-%m-%d.log"
    # INFO文件处理器（记录所有级别）
    file_handler_info = CustomTimedRotatingFileHandler(
        files_path_log_info,
        when="midnight",
        interval=1,
        backupCount=14,
        custom_function=external_custom_function,
    )
    file_handler_info.setFormatter(formatter)
    if is_dev:
        # file_handler_info.setLevel(logging.DEBUG)
        file_handler_info.setLevel(logging.INFO)
    else:
        file_handler_info.setLevel(logging.WARN)  # 记录所有级别
    logger.addHandler(file_handler_info)

    # ERROR文件处理器（只记录ERROR及以上）
    file_handler_error = CustomTimedRotatingFileHandler(
        files_path_log_error,
        # 日志切割时间
        when="midnight",
        interval=1,
        # 保留天数
        backupCount=14,
        # 自定义切换调用函数
        custom_function=external_custom_function,
    )
    file_handler_error.setFormatter(formatter)
    file_handler_error.setFormatter(formatter)
    file_handler_error.setLevel(logging.ERROR)  # 只记录ERROR及以上
    logger.addHandler(file_handler_error)


# 配置
setup_logging()
# 生成
logger = logging.getLogger()
# 输出带颜色的日志
logger.info("%s %s", "ok...log配置", "多log")
logger.error("%s %s", "ok...error...log配置", "error log测试")
