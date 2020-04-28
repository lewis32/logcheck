import os
import json
import logging

log = logging.getLogger(__name__)


class Config:
    def __init__(self, dict_):
        self._stop_cmd = dict_['serial_config']['stop_cmd']
        self._start_cmd = dict_['serial_config']['start_cmd']
        self._kafka_server = dict_['kafka_config']['server']
        self._kafka_topic = dict_['kafka_config']['topic']
        self._kafka_group_id = dict_['kafka_config']['group_id']
        self._kafka_filter = dict_['kafka_config']['filter']
        self._ssh_enable = dict_['kafka_config']['ssh_enable']
        self._ssh_host = dict_['kafka_config']['ssh_config']['host']
        self._ssh_port = dict_['kafka_config']['ssh_config']['port']
        self._ssh_user = dict_['kafka_config']['ssh_config']['user']
        self._ssh_pwd = dict_['kafka_config']['ssh_config']['pwd']
        self._mode = dict_['mode']

    def to_dict(self):
        return {
            'serial_config': {
                'start_cmd': self._start_cmd,
                'stop_cmd': self._stop_cmd
            },
            'kafka_config': {
                'server': self._kafka_server,
                'topic': self._kafka_topic,
                'group_id': self._kafka_group_id,
                'filter': self._kafka_filter,
                'ssh_enable': self._ssh_enable,
                'ssh_config': {
                    'host': self._ssh_host,
                    'port': self._ssh_port,
                    'user': self._ssh_user,
                    'pwd': self._ssh_pwd
                }
            },
            'mode': self._mode
        }

    @property
    def stop_cmd(self):
        return self._stop_cmd

    @stop_cmd.setter
    def stop_cmd(self, value):
        self._stop_cmd = value

    @property
    def start_cmd(self):
        return self._start_cmd

    @start_cmd.setter
    def start_cmd(self, value):
        self._start_cmd = value

    @property
    def kafka_server(self):
        return self._kafka_server

    @kafka_server.setter
    def kafka_server(self, value):
        self._kafka_server = value

    @property
    def kafka_topic(self):
        return self._kafka_topic

    @kafka_topic.setter
    def kafka_topic(self, value):
        self._kafka_topic = value

    @property
    def kafka_group_id(self):
        return self._kafka_group_id

    @kafka_group_id.setter
    def kafka_group_id(self, value):
        self._kafka_group_id = value

    @property
    def kafka_filter(self):
        return self._kafka_filter

    @kafka_filter.setter
    def kafka_filter(self, value):
        self._kafka_filter = value

    @property
    def ssh_enable(self):
        return self._ssh_enable

    @ssh_enable.setter
    def ssh_enable(self, value):
        self._ssh_enable = value

    @property
    def ssh_host(self):
        return self._ssh_host

    @ssh_host.setter
    def ssh_host(self, value):
        self._ssh_host = value

    @property
    def ssh_port(self):
        return self._ssh_port

    @ssh_port.setter
    def ssh_port(self, value):
        self._ssh_port = value

    @property
    def ssh_user(self):
        return self._ssh_user

    @ssh_user.setter
    def ssh_user(self, value):
        self._ssh_user = value

    @property
    def ssh_pwd(self):
        return self._ssh_pwd

    @ssh_pwd.setter
    def ssh_pwd(self, value):
        self._ssh_pwd = value

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = value


class LoadConfig:
    _config_path = os.path.join(
        os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.realpath(__file__))))),
        'conf',
        'setting.json'
    )

    @classmethod
    def get_config(cls):
        with open(cls._config_path, 'r+', encoding='utf-8') as f:
            obj = json.load(f, cls=ConfigDecode)
            log.info("get config file...")
            return obj

    @classmethod
    def set_config(cls, obj):
        with open(cls._config_path, 'w+', encoding='utf-8') as f:
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

