#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
import time
import bisect
# import sys
# sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'package'))
# from myconfigparser import MyConfigParser as ConfigParser
from .package.myconfigparser import MyConfigParser as ConfigParser


class LogCheck():
    filepath = os.path.abspath((os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
    stime = time.strftime('%Y%m%d-%H%M%S', time.localtime())

    def __init__(self):
        self.conflist = self._load_policy()

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

        conf = ConfigParser()
        conf.read(os.path.join(self.filepath, 'conf', 'policy.ini'), encoding='utf-8')
        return conf

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

    def _compare_log(self, log, conflist):
        """
        check log value with the pattern in policy file
        :param log:
        :param conflist:
        :return:
        """
        res = {
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

        try:
            conf = dict(conflist.items('_'.join(title)) + conflist.items('common'))

        except Exception as e:
            res['result'] = 1
            print("Failed to combine common keys with event keys : ", e)

        else:
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

            if len(res['missing_key']) or len(res['undefined_key']) or len(res['invalid_key']):
                res['result'] = 1

        finally:
            return res

    # def _compare_timestamp(self, log):
    #     """
    #     only for the key timestamp
    #     :param log:
    #     :return:
    #     """
    #     st, et = 1, 2
    #
    #     for key in log:
    #         if self._to_lower_key(key) == 'starttime': st = log[key]
    #         if self._to_lower_key(key) == 'endtime': et = log[key]
    #
    #     if et != '0' and st >= et:
    #         return 1

    def _to_lower_key(self, key):
        return key.lower()

    def check_log(self, data=None):
        """
        main func
        :return: log data and check result
        """
        if not data:
            return

        output_name = 'result-%s.txt' % self.stime

        if not os.path.exists(os.path.join(self.filepath, 'result')):
            os.mkdir(os.path.join(self.filepath, 'result'))
        output_path = os.path.join(self.filepath, 'result', output_name)

        with open(output_path, 'w', encoding='utf-8') as f:
            listed_data = self._split_log(data)
            results = []

            for log in listed_data:
                ret = self._compare_log(log, self.conflist)
                results.append(ret)
            json.dump(results, f, indent=4)

            return listed_data, results
