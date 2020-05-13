import logging


class MyLogging:
    # logging.basicConfig(level=logging.INFO,
    #                     filename='log.txt',
    #                     filemode='w',
    #                     format='[%(asctime)s] [%(levelname)s] [%(name)s: %(lineno)s] -- [%(funcName)s] %(message)s')
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s] [%(levelname)s] [%(name)s: %(lineno)s] -- [%(funcName)s] %(message)s')

    @staticmethod
    def getLogger(name):
        global log
        log = logging.getLogger(name)
        # log.setLevel(logging.INFO)
        # format_ = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s: %(lineno)s] -- [%(funcName)s] %(message)s')
        # sh = logging.StreamHandler()
        # sh.setFormatter(format_)
        # fh = logging.FileHandler(filename='log.txt',
        #                          mode='w',
        #                          encoding='utf-8')
        # fh.setFormatter(format_)
        # log.addHandler(sh)
        # log.addHandler(fh)

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
