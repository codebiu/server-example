import logging
import logging.config
#默认的warning级别，只输出warning以上的
#使用basicConfig()来指定日志级别和相关信息
from config.path import files_path_log
from config.index import conf
from utils.enum.color import Color
from utils.log.ColoredConsoleHandler import ColoredConsoleHandler
from utils.log.CustomTimedRotatingFileHandler import CustomTimedRotatingFileHandler

'''
    生成文件log和带颜色控制台log
'''
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
# 格式
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# 控制台log
debug_handler = ColoredConsoleHandler()
debug_handler.setFormatter(formatter)

# 文件log
error_handler = CustomTimedRotatingFileHandler(
    'error_%Y-%m-%d.log', when='midnight', interval=1, backupCount=7, custom_function=external_custom_function
)

debug_handler.setLevel(logging.DEBUG)
error_handler.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
debug_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)

logger.addHandler(debug_handler)
logger.addHandler(error_handler)


def external_custom_function():
    '''每日log额外处理'''
    print("new log.")

# 输出带颜色的日志
logger.debug('...log配置完成')


