import os
import json
import logging

log = logging.getLogger(__name__)


class Config:
    def __init__(self, dict_):
        self.stop_cmd = dict_['serial_config']['stop_cmd']
        self.start_cmd = dict_['serial_config']['start_cmd']
        self.kafka_server = dict_['kafka_config']['server']
        self.kafka_topic = dict_['kafka_config']['topic']
        self.kafka_group_id = dict_['kafka_config']['group_id']
        self.kafka_filter = dict_['kafka_config']['filter']
        self.ssh_enable = dict_['kafka_config']['ssh_enable']
        self.ssh_host = dict_['kafka_config']['ssh_config']['host']
        self.ssh_port = dict_['kafka_config']['ssh_config']['port']
        self.ssh_user = dict_['kafka_config']['ssh_config']['user']
        self.ssh_pwd = dict_['kafka_config']['ssh_config']['pwd']
        self.mode = dict_['mode']

    def to_dict(self):
        return {
            'serial_config': {
                'start_cmd': self.start_cmd,
                'stop_cmd': self.stop_cmd
            },
            'kafka_config': {
                'server': self.kafka_server,
                'topic': self.kafka_topic,
                'group_id': self.kafka_group_id,
                'filter': self.kafka_filter,
                'ssh_enable': self.ssh_enable,
                'ssh_config': {
                    'host': self.ssh_host,
                    'port': self.ssh_port,
                    'user': self.ssh_user,
                    'pwd': self.ssh_pwd
                }
            },
            'mode': self.mode
        }


class LoadConfig:
    def __init__(self):
        self._config_path = os.path.join(
            os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.realpath(__file__))))),
            'conf',
            'setting.json'
        )

    def get_config(self):
        with open(self._config_path, 'r+', encoding='utf-8') as f:
            obj = json.load(f, cls=ConfigDecode)
            log.info("get config file...")
            return obj

    def set_config(self, obj):
        with open(self._config_path, 'w+', encoding='utf-8') as f:
            json.dump(obj, f, cls=ConfigEncode, ensure_ascii=False, indent=4,
                      sort_keys=True)
            log.info("set config file...")


class ConfigDecode(json.JSONDecoder):
    def decode(self, s):
        dict_ = super().decode(s)
        return Config(dict_)


class ConfigEncode(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Config):
            return o.to_dict()
        return json.JSONEncoder.default(o)


if __name__ == '__main__':
    try:
        lc = LoadConfig()
        config = lc.get_config()
        lc.set_config(config)
    except Exception as e:
        print(str(e))

