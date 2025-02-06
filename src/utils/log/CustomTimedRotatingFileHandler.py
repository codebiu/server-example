import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename_pattern, when, interval, backupCount, custom_function=None):
        # 使用当前时间格式化文件名作为初始文件名
        initial_filename = datetime.now().strftime(filename_pattern)
        super().__init__(initial_filename, when, interval, backupCount)
        
        self.filename_pattern = filename_pattern  # 保存文件名模板
        self.custom_function = custom_function  # 保存外部传入的函数

    def doRollover(self):
        if self.custom_function:
            self.custom_function()

        # 根据当前时间生成新的文件名
        new_filename = datetime.now().strftime(self.filename_pattern)
        self.baseFilename = new_filename
        
        # 调用基类的方法完成实际的日志滚动
        super().doRollover()

if __name__ == '__main__':
    def external_custom_function():
        print("Custom function called when the log file is rolled over.")

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    debug_handler = CustomTimedRotatingFileHandler(
        'd:\\debug_%Y-%m-%d.log', when='midnight', interval=1, backupCount=7, custom_function=external_custom_function
    )
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

    logger.debug("This is a debug message")
    logger.error("This is an error message")