#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
import sys
import time
import bisect
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'package'))
from myconfigparser import MyConfigParser as ConfigParser


class LogCheck():

    filepath = os.path.abspath((os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
    stime = time.strftime('%Y%m%d-%H%M%S', time.localtime())

    def __init__(self):
        self.conflist = self._load_policy()

    def _load_log(self):
        with open(os.path.join(self.filepath, 'conf', 'log.txt'), 'r') as f:
            loglist = []
            text = f.read()
            pattern = re.compile(r'{.*?}')
            for item in pattern.findall(text):
                item = json.loads(item)
                loglist.append(item)
            return loglist

    def _load_policy(self):
        conf = ConfigParser()
        conf.read(os.path.join(self.filepath, 'conf', 'policy.ini'), encoding='utf-8')
        return conf

    def _compare_keys(self, log, conf):
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
        result = {
                    'src_event_code': None,
                    'event_code': None,
                    'missing_key': [],
                    'undefined_key': {},
                    'invalid_key': {},
                    'result': 0
                    }
        count = len(log)
        n = 1
        for key in log:
            if self._to_lower_key(key) != 'eventcode' and n < count:
                n += 1
                continue
            elif self._to_lower_key(key) != 'eventcode' and n == count:
                result['missing_key'].append('eventcode')
                break
            else:
                try:
                    conf = dict(conflist.items(log[key]) + conflist.items('common'))
                except Exception as e:
                    print("Failed to combine common keys with event keys : ", e)
                    invalid_mutual_dict = {}
                    break
                else:
                    result['event_code'] = log[key]
                    for i in conf:
                        conf[self._to_lower_key(i)] = conf.pop(i)
                    mutual_key,log_key,conf_key = self._compare_keys(log,conf)
                    if len(log_key) != 0:
                        for k in log_key:
                            result['undefined_key'][k] = log[k]
                    if len(conf_key) != 0:
                        for k in conf_key:
                            result['missing_key'].append(k)
                    mutual_dict = {}
                    invalid_mutual_dict = {}
                    for i in mutual_key:
                        mutual_dict[i] = conf[self._to_lower_key(i)]
                        if not re.match(eval(mutual_dict[i]), str(log[i])):
                            invalid_mutual_dict[i] = log[i]
                    if self._compare_timestamp(log) == 1:
                        result['invalid_key']['StartTime'] = 'EndTime'
            if len(invalid_mutual_dict) > 0:
                result['invalid_key'] = dict(result['invalid_key'], **invalid_mutual_dict)
            if not (len(result['missing_key']) == 0 and len(result['undefined_key']) == 0 and len(result['invalid_key'])) == 0:
                result['result'] = 1
        print(result)
        return result


    def _compare_timestamp(self, log):
        st, et = 1, 2
        for key in log:
            if self._to_lower_key(key) == 'starttime':st = log[key]
            if self._to_lower_key(key) == 'endtime':et = log[key]
        if et != '0' and st >= et:
            return 1

    def _to_lower_key(self, key):
        return key.lower()

    def check_log(self):
        try:
            loglist = self._load_log()
        except Exception as e:
            print("Failed to load log or policy: ", e)
        else:
            output_name = 'result-%s.txt' % self.stime
            if not os.path.exists(os.path.join(self.filepath, 'result')):
                os.mkdir(os.path.join(self.filepath, 'result'))
            output_path = os.path.join(self.filepath, 'result', output_name)
            with open(output_path, 'w', encoding='utf-8') as f:
                results = []
                for log in loglist:
                    ret = self._compare_log(log, self.conflist)
                    results.append(ret)
                json.dump(results, f, indent=4)
                return results



