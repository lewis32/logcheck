import logging


class MyLogging:
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s] [%(levelname)s] [%(name)s: %(lineno)s] -- [%(funcName)s] %(message)s', )

    @staticmethod
    def getLogger(name):
        global log
        log = logging.getLogger(name)
        return log

    @staticmethod
    def error(msg):
        log.error(msg)

    @staticmethod
    def warning(msg):
        log.warning(msg)

    @staticmethod
    def debug(msg):
        log.debug(msg)

    @staticmethod
    def info(msg):
        log.info(msg)
