#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import re
import json
import time
import bisect
from .package.mylogging import MyLogging as Logging


class LogCheck:
    filepath = os.path.abspath((os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
    stime = time.strftime('%Y%m%d-%H%M%S', time.localtime())

    def __init__(self):
        self.logger = Logging(__name__)
        self.policy_all = self._load_policy()

    def _split_log(self, raw_str):
        """
        split log stream to json array
        :param raw_str:
        :return:
        """

        stack_left_bracket = []
        stack_right_bracket = []
        array_json = []
        for i in range(len(raw_str)):
            if raw_str[i] == '{':
                stack_left_bracket.append(i)
            if raw_str[i] == '}':
                stack_right_bracket.append(i)
            if stack_left_bracket and len(stack_left_bracket) == len(
                    stack_right_bracket):
                array_json.append(raw_str[stack_left_bracket[0]: stack_right_bracket.pop() + 1])
                stack_left_bracket = []
                stack_right_bracket = []
        return array_json

    def _load_policy(self):
        """
        load policy file
        :return:
        """
        policy_path = os.path.os.path.join(self.filepath, 'conf')
        policy_common = None
        policy_module = {}

        for i in os.listdir(policy_path):
            if re.match(r'^policy_module', i):
                policy_module_path = os.path.os.path.join(policy_path, i)
                with open(policy_module_path, mode='r', encoding='utf-8') as f:
                    str_policy = f.read()
                    if str_policy.startswith(u'\ufeff'):
                        str_policy = str_policy.encode('utf-8')[3:].decode('utf-8')
                    dict_policy = json.loads(str_policy, encoding='utf-8')
                    policy_module = dict(policy_module, **dict_policy)
            if re.match(r'^policy_common', i):
                policy_common_path = os.path.os.path.join(policy_path, i)
                with open(policy_common_path, mode='r', encoding='utf-8') as f:
                    str_policy = f.read()
                    if str_policy.startswith(u'\ufeff'):
                        str_policy = str_policy.encode('utf-8')[3:].decode('utf-8')
                    policy_common = json.loads(str_policy, encoding='utf-8')

        if policy_common and policy_module:
            for event in policy_module:
                print(event)
                m = re.match(r'^(null|\d+)_(\d+)_([\d.]+)', event)
                if m.group(0):
                    if m.group(1) != 'null':
                        policy_module[event]['keys']['srceventcode'] = {
                            'regex': m.group(1),
                            'alias': '上级事件'
                        }
                    policy_module[event]['keys']['eventcode'] = {
                        'regex': m.group(2),
                        'alias': '本级事件'
                    }
                    policy_module[event]['keys']['version'] = {
                        'regex': m.group(3),
                        'alias': '日志版本'
                    }
                for ex in policy_module[event]['no_common_keys']:
                    if ex in policy_common:
                        policy_common.pop(ex)
                    else:
                        self.logger.error('%s的限制公共字段不在公共字段内！' % (event,))
                policy_module[event]['keys'] = dict(policy_module[event]['keys'], **policy_common)
            self.logger.info(json.dumps(policy_module))
            return policy_module

    def _compare_keys(self, log, conf):
        """
        find mutual keys, extra keys and missing keys in log
        :param log:
        :param conf:
        :return:
        """

        mutual_key = []
        mutual_key_lower = []

        log = [i for i in log]
        conf = [i for i in conf]
        conf.sort()

        for i in log:
            pos = bisect.bisect_left(conf, self._to_lower_key(i))
            if pos < len(conf) and conf[pos] == self._to_lower_key(i):
                mutual_key.append(i)
                mutual_key_lower.append(self._to_lower_key(i))

        mutual_key = list(set(mutual_key))
        mutual_key_lower = list(set(mutual_key_lower))
        log_key = list(set(log).difference(set(mutual_key)))
        conf_key = list(set(conf).difference(set(mutual_key_lower)))

        return mutual_key, log_key, conf_key

    def _compare_log(self, log, conf):
        """
        check log value with the pattern in policy file
        :param log:
        :param conflist:
        :return:
        """
        res = {
            'data': log,
            'src_event_code': None,
            'event_code': None,
            'missing_key': [],
            'undefined_key': {},
            'invalid_key': {},
            'result': 0
        }

        # count = len(log)
        # n = 1
        title = ['null', 'null', 'null']

        for key in log:
            lower_key = self._to_lower_key(key)
            if lower_key == 'srceventcode':
                title[0] = log[key]
                res['src_event_code'] = log[key]
            if lower_key == 'eventcode':
                title[1] = log[key]
                res['event_code'] = log[key]
            if lower_key == 'version':
                title[2] = log[key]
                # res['version'] = log[key]

        for i in conf:
            conf[self._to_lower_key(i)] = conf.pop(i)

        mutual_key, log_key, conf_key = self._compare_keys(log, conf)
        if len(log_key):
            for key in log_key:
                res['undefined_key'][key] = log[key]
        if len(conf_key):
            for key in conf_key:
                res['missing_key'].append(key)

        mutual_dict = {}
        invalid_mutual_dict = {}
        for i in mutual_key:
            mutual_dict[i] = conf[self._to_lower_key(i)]
            if not re.match(eval(mutual_dict[i]), str(log[i])):
                invalid_mutual_dict[i] = log[i]

        if len(invalid_mutual_dict):
            res['invalid_key'] = {**res['invalid_key'], **invalid_mutual_dict}

        if len(res['missing_key']) or len(res['invalid_key']):
            res['result'] = 1
        elif len(res['undefined_key']):
            res['result'] = 2

            return res

    def _to_lower_key(self, key):
        return key.lower()

    def check_log(self, data=None):
        """
        main func
        :return: listed_data dict, listed_result list
        """
        if not data:
            return

        output_name = 'result-%s.txt' % self.stime

        if not os.path.exists(os.path.join(self.filepath, 'result')):
            os.mkdir(os.path.join(self.filepath, 'result'))
        output_path = os.path.join(self.filepath, 'result', output_name)

        with open(output_path, 'w', encoding='utf-8') as f:
            listed_data = self._split_log(data)
            listed_results = []

            for data in listed_data:
                try:
                    data = json.loads(data)
                except json.decoder.JSONDecodeError as e:
                    self.logger.error("Error occurs while decoding JSON: " + str(e))
                else:
                    if "eventcode" not in data:
                        continue
                    ret = self._compare_log(data, self.conflist)
                    listed_results.append(ret)
            json.dump(listed_results, f, indent=4)

            return listed_results

    def log_policy(self):
        self._load_policy()
