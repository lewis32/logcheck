import json
from .mylogging import MyLogging


class MyJsonParser:
    def __init__(self, file):
        self.logger = MyLogging(__name__)
        with open(file) as f:
            try:
                self.dict = json.load(f)
            except Exception as e:
                self.logger.error(str(e))
            else:
                self.dict = None

    def json2dict(self):
        return self.dict
