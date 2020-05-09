#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
import time
import bisect
from .package.mylogging import MyLogging as Logging

log = Logging.getLogger(__name__)


class LogCheck:
    filepath = os.path.abspath((os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
    stime = time.strftime('%Y%m%d-%H%M%S', time.localtime())

    def __init__(self):
        # self.logger = Logging(__name__)
        self.policy_all = self._load_policy()

    def _split_log(self, raw_str):
        """
        对源日志数据按照JSON格式进行截取
        :param raw_str: str
        :return: list
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
        处理配置文件
        :return: dict
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
                m = re.match(r'^(null|\d+)_(\d+)_([\d.]+)', event)
                if m.group(0):
                    if m.group(1) != 'null':
                        policy_module[event]['keys']['srceventcode'] = {
                            'regex': m.group(1),
                            'key_alias': '上级事件'
                        }
                    policy_module[event]['keys']['eventcode'] = {
                        'regex': m.group(2),
                        'key_alias': '本级事件'
                    }
                    policy_module[event]['keys']['version'] = {
                        'regex': m.group(3),
                        'key_alias': '日志版本'
                    }
                for ex in policy_module[event]['ignore_keys']:
                    if ex in policy_common:
                        policy_common.pop(ex)
                    if ex in policy_module:
                        policy_module[event]['keys'].pop(ex)
                    else:
                        log.error('找不到限制字段%s！' % (ex,))
                policy_module[event]['keys'] = dict(policy_module[event]['keys'], **policy_common)
            log.info("policy: " + json.dumps(policy_module))
            return policy_module

    def _compare_keys(self, data, conf):
        """
        查找日志中重复、多余和缺失的字段
        :param data: dict
        :param conf: dict
        :return: list, list, list
        """

        mutual_key = []
        mutual_key_lower = []

        data = [i for i in data]
        conf = [i for i in conf]
        log.info("conf" + str(conf))
        conf.sort()

        for i in data:
            pos = bisect.bisect_left(conf, (lambda x: x.lower())(i))
            if pos < len(conf) and conf[pos] == (lambda x: x.lower())(i):
                mutual_key.append(i)
                mutual_key_lower.append((lambda x: x.lower())(i))

        mutual_key = list(set(mutual_key))
        mutual_key_lower = list(set(mutual_key_lower))
        data_key = list(set(data).difference(set(mutual_key)))
        conf_key = list(set(conf).difference(set(mutual_key_lower)))

        return mutual_key, data_key, conf_key

    def _compare_log(self, data, conf):
        """
        根据配置文件的正则对日志数据进行对比
        :param data: dict
        :param conf: dict
        :return: dict
        """
        res = {
            'data': {},
            'src_event_code': None,
            'event_code': None,
            'event_alias': None,
            'missing_key': {},
            'undefined_key': {},
            'invalid_key': {},
            'result': 0
        }

        # count = len(data)
        # n = 1
        title = ['null', 'null', 'null']

        for key in data:
            lower_key = (lambda x: x.lower())(key)
            if lower_key == 'srceventcode':
                title[0] = data[key]
                res['src_event_code'] = data[key]
            if lower_key == 'eventcode':
                title[1] = data[key]
                res['event_code'] = data[key]
            if lower_key == 'version':
                title[2] = data[key]
                # res['version'] = data[key]
        title = '_'.join(title)

        if title not in conf:
            # 找不到对应事件，直接返回-1
            for key in data:
                res['data'][key] = {}
                res['data'][key]['value'] = data[key]
            res['result'] = -1
            return res

        if conf[title]['event_alias'].strip() != '':
            res['event_alias'] = conf[title]['event_alias']

        for i in conf[title]['keys']:
            conf[title]['keys'][(lambda x:x.lower())(i)] = conf[title]['keys'].pop(i)

        mutual_key, data_key, conf_key = self._compare_keys(data, conf[title]['keys'])
        log.info('mutual key:' + str(mutual_key))
        log.info('conf_key:' + str(conf_key))
        if len(data_key):
            for key in data_key:
                res['undefined_key'][key] = {}
                res['undefined_key'][key]['value'] = data[key]
                res['data'][key] = {}
                res['data'][key]['value'] = data[key]
        if len(conf_key):
            for key in conf_key:
                res['missing_key'][key] = {}
                res['missing_key'][key]['key_alias'] = conf[title]['keys'][key]['key_alias']

        mutual_dict = {}
        invalid_mutual_dict = {}
        for i in mutual_key:
            mutual_dict[i] = conf[title]['keys'][(lambda x: x.lower())(i)]
            res['data'][i] = {}
            res['data'][i]['value'] = data[i]
            res['data'][i]['key_alias'] = conf[title]['keys'][(lambda x: x.lower())(i)]['key_alias']
            # if not re.match(eval(mutual_dict[i]['regex']), str(data[i])):
            if not re.match(mutual_dict[i]['regex'], str(data[i])):
                invalid_mutual_dict[i] = {}
                invalid_mutual_dict[i]['value'] = data[i]
                invalid_mutual_dict[i]['key_alias'] = conf[title]['keys'][key]['key_alias']
                # invalid_mutual_dict[i] = data[i]

        if len(invalid_mutual_dict):
            res['invalid_key'] = dict(**res['invalid_key'], **invalid_mutual_dict)

        # 存在策略中未定义的键值，返回2
        if len(res['undefined_key']):
            res['result'] = 2

        # 存在不合法键值或丢失键值，返回1
        if len(res['missing_key']) or len(res['invalid_key']):
            res['result'] = 1

        return res

    def _to_lower_key(self, key):
        """
        转化小写，不影响原数据
        :param key: str
        :return: str
        """
        return key.lower()

    def check_log(self, data=None, filter=None):
        """
        对比日志
        :param data: str
        :return: listed_results list
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
                    log.error("Error occurs while decoding JSON: " + str(e))
                else:
                    if "eventcode" not in data or (filter and filter in data):
                        continue
                    try:
                        ret = self._compare_log(data, self.policy_all)
                    except Exception as e:
                        log.error(str(e))
                    listed_results.append(ret)
            json.dump(listed_results, f, indent=4)
            log.info(json.dumps(listed_results))

            return listed_results

    def load_policy(self):
        self._load_policy()
