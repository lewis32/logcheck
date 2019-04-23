import os
import re
import json
import sys
import time
import bisect
sys.path.append(os.path.dirname(os.path.realpath(__file__))+'\\package')
import myconfigparser


class LogCheck():

    filepath = os.path.abspath((os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
    ltime = time.localtime()
    stime = time.strftime('%Y%m%d-%H%M%S', ltime)

    def __init__(self):
        pass

    def load_log(self):
        with open(self.filepath+'\\conf\\log.xml','r') as f:
            loglist = []
            text = f.read()
            pattern = re.compile(r'{.*?}')
            for item in pattern.findall(text):
                item = json.loads(item)
                loglist.append(item)
            return loglist

    def load_policy(self):
        conf = myconfigparser.MyConfigParser()
        conf.read(self.filepath+r'\\conf\\policy.ini',encoding='utf-8')
        return conf

    def compare_keys(self, log, conf):
        mutual_key = []
        mutual_key_lower = []
        log = [i for i in log]
        conf = [i for i in conf]
        conf.sort()
        for i in log:
            pos = bisect.bisect_left(conf, self.to_lower_key(i))
            if pos < len(conf) and conf[pos] == self.to_lower_key(i):
                mutual_key.append(i)
                mutual_key_lower.append(self.to_lower_key(i))
        mutual_key = list(set(mutual_key))
        mutual_key_lower = list(set(mutual_key_lower))
        log_key = list(set(log).difference(set(mutual_key)))
        conf_key = list(set(conf).difference(set(mutual_key_lower)))
        return mutual_key, log_key, conf_key

    def compare_timestamp(self, log):
        st, et = 1, 2
        for key in log:
            if self.to_lower_key(key) == 'starttime':st = log[key]
            if self.to_lower_key(key) == 'endtime':et = log[key]
        if et != '0' and st >= et:
            return 1

    def to_lower_key(self, key):
        return key.lower()

    def check_log(self):
        try:
            loglist = self.load_log()
            conflist = self.load_policy()
        except Exception as e:
            print("Failed to load log or policy: ", e)
        else:
            with open(self.filepath+r'\\result\\result-'+self.stime+'.txt', 'w', encoding='utf-8') as f:
                result = []
                for log in loglist:
                    count = len(log)
                    n = 1
                    f.writelines(['-****************** Begin ******************-\n'])
                    result.append('-****************** Begin ******************-\n')
                    for key in log:
                        if self.to_lower_key(key) != 'eventcode' and n < count:
                            n += 1
                            continue
                        elif self.to_lower_key(key) != 'eventcode' and n == count:
                            f.writelines(['Missing key: eventcode\n'])
                            result.append('Missing key: eventcode\n')
                            break
                        else:
                            try:
                                conf = dict(conflist.items(log[key]) + conflist.items('common'))
                            except Exception as e:
                                print("Failed to combine common keys with event keys : ", e)
                            else:
                                f.writelines(['Eventcode: ', log[key], '\n'])
                                result.append('Eventcode: ' + log[key] + '\n')
                                for i in conf:
                                    conf[self.to_lower_key(i)] = conf.pop(i)
                                mutual_key,log_key,conf_key = self.compare_keys(log,conf)
                                if len(log_key) != 0:
                                    f.writelines(['Undefined key: ', str(log_key), '\n'])
                                    result.append('Undefined key: ' + str(log_key) + '\n')
                                if len(conf_key) != 0:
                                    f.writelines(['Missing key: ', str(conf_key), '\n'])
                                    result.append('Missing key: ' + str(conf_key) + '\n')
                                mutual_dict = {}
                                invalid_mutual_dict = {}
                                for i in mutual_key:
                                    mutual_dict[i] = conf[self.to_lower_key(i)]
                                    if not re.match(eval(mutual_dict[i]), str(log[i])):
                                        invalid_mutual_dict[i] = log[i]
                                if self.compare_timestamp(log) == 1:
                                    f.writelines(['Invalid key-value: StartTime >= EndTime\n'])
                                    result.append('Invalid key-value: StartTime >= EndTime\n')
                    if len(invalid_mutual_dict) > 0:
                        f.writelines(['Invalid key-value: ',str(invalid_mutual_dict), '\n'])
                        result.append('Invalid key-value: ' + str(invalid_mutual_dict) + '\n')
                    f.writelines(['-******************* End *******************-\n\n'])
                    result.append('-******************* End *******************-\n\n')
                return result



