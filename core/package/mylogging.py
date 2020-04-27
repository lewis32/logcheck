import time
import logging
from logging.handlers import TimedRotatingFileHandler

print_level = logging.DEBUG    # 打印级别控制
file_path = "D:/"        # 定义日志存放路径
file_name = time.strftime('%Y%m%d', time.localtime(time.time()))  # 文件名称


class Log:
    # 构造函数
    def __init__(self, name):
        self.filename = file_path + file_name + '.log'  # 日志文件名称
        self.name = name  # 为%(name)s赋值

        # 创建日志器
        self.logger = logging.getLogger(self.name)

        # 控制记录级别
        self.logger.setLevel(print_level)

        # 控制台日志
        self.console_handler = logging.StreamHandler()
        console_format = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s[line:%(lineno)d] - %(message)s')
        self.console_handler.setFormatter(console_format)

        # 文件日志
        self.filetime_handler = TimedRotatingFileHandler(self.filename, 'D', 1, 30) #保留30天,1月保存一个文件
        file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s[line:%(lineno)d] - %(message)s')
        self.filetime_handler.setFormatter(file_format)

        # 为logger添加的日志处理器
        self.logger.addHandler(self.console_handler)
        self.logger.addHandler(self.filetime_handler)

    # 测试
    def debug(self, msg):
        self.logger.debug(msg)

    # 信息
    def info(self, msg):
        self.logger.info(msg)

    # 警告
    def warning(self, msg):
        self.logger.warning(msg)

    # 错误
    def error(self, msg):
        self.logger.error(msg)

    # 重大错误
    def critical(self, msg):
        self.logger.critical(msg)

    # 抛出异常
    def exception(self, msg):
        self.logger.exception(msg)

    # 关闭控制台日志
    def close_console(self):
        self.logger.removeHandler(self.console_handler)

    # 关闭文件日志
    def close_filetime(self):
        self.logger.removeHandler(self.filetime_handler)