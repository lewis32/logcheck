#!/usr/bin/env Python
# coding=utf-8
import logging


class MyLogging:
    def __init__(self, name):
        logging.basicConfig(level=logging.DEBUG,
                            format='[%(asctime)s] [%(levelname)s] [%(name)s: %(lineno)s] - %(message)s')
        self.logger = logging.getLogger(name=name)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)
