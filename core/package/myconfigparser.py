from configparser import *


class MyConfigParser(ConfigParser):
    def __init__(self, filename=None):
        super().__init__()
        self.filename = filename
        self.read(filename)

    def get(self, section, option, *args, **kwargs):
        super().get(section, option, *args, **kwargs)

    def set(self, *args, **kwargs):
        super().set(*args, **kwargs)
        with open(self.filename) as f:
            super().write(f)

    def optionxform(self, optionstr):
        return optionstr
