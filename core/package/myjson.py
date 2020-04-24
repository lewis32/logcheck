import json
import logging

log = logging.getLogger(__name__)


class MyJsonParser:
    def __init__(self, file):
        with open(file) as f:
            try:
                self.dict = json.load(f)
            except Exception as e:
                log.error(str(e))
            else:
                self.dict = None

    def json2dict(self):
        return self.dict
