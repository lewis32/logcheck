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

    def loadLog(self):
        with open(self.filepath+'\\conf\\log.xml','r') as f:
            loglist = []
            text = f.read()
            pattern = re.compile(r'{.*?}')
            for item in pattern.findall(text):
                item = json.loads(item)
                loglist.append(item)
            return loglist

    def loadPolicy(self):
        conf = myconfigparser.MyConfigParser()
        conf.read(self.filepath+r'\\conf\\policy.ini',encoding='utf-8')
        return conf

    def compareKeys(self,log,conf):
        mutual_key = []
        mutual_key_lower = []
        log = [i for i in log]
        conf = [i for i in conf]
        conf.sort()
        for i in log:
            pos = bisect.bisect_left(conf,self.lowerKeys(i))
            if pos < len(conf) and conf[pos] == self.lowerKeys(i):
                mutual_key.append(i)
                mutual_key_lower.append(self.lowerKeys(i))
        mutual_key = list(set(mutual_key))
        mutual_key_lower = list(set(mutual_key_lower))
        log_key = list(set(log).difference(set(mutual_key)))
        conf_key = list(set(conf).difference(set(mutual_key_lower)))
        return mutual_key,log_key,conf_key

    def compareTimestamp(self,log):
        st, et = 1, 2
        for key in log:
            if self.lowerKeys(key) == 'starttime':st = log[key]
            if self.lowerKeys(key) == 'endtime':et = log[key]
        if et != '0' and st >= et:
            return 1

    def lowerKeys(self,key):
        return key.lower()

    def checkLog(self):
        try:
            loglist = self.loadLog()
            conflist = self.loadPolicy()
        except Exception as e:
            print("Failed to load log or policy: ",e)
        else:
            with open(self.filepath+r'\\result\\result-'+self.stime+'.txt','w',encoding='utf-8' ) as f:
                for log in loglist:
                    count = len(log)
                    n = 1
                    f.writelines(['****************** Begin ******************\n'])
                    for key in log:
                        if self.lowerKeys(key) != 'eventcode' and n < count:
                            n += 1
                            continue
                        elif self.lowerKeys(key) != 'eventcode' and n == count:
                            f.writelines(['Missing key: eventcode\n'])
                            break
                        else:
                            try:
                                conf = dict(conflist.items(log[key]) + conflist.items('common'))
                            except Exception as e:
                                print("Failed to combine common keys with event keys : ",e)
                            else:
                                f.writelines(['Eventcode: ',log[key],'\n'])
                                for i in conf:
                                    conf[self.lowerKeys(i)] = conf.pop(i)
                                mutual_key,log_key,conf_key = self.compareKeys(log,conf)
                                if len(log_key) != 0:
                                    f.writelines(['Undefined key: ',str(log_key),'\n'])
                                if len(conf_key) != 0:
                                    f.writelines(['Missing key: ',str(conf_key),'\n'])
                                mutual_dict = {}
                                invalid_mutual_dict = {}
                                for i in mutual_key:
                                    mutual_dict[i] = conf[self.lowerKeys(i)]
                                    if not re.match(eval(mutual_dict[i]),str(log[i])):
                                        invalid_mutual_dict[i] = log[i]
                                if self.compareTimestamp(log) == 1:
                                    f.writelines(['Invalid key-value: StartTime >= EndTime\n'])
                    if len(invalid_mutual_dict) > 0:
                        f.writelines(['Invalid key-value: ',str(invalid_mutual_dict),'\n'])
                    f.writelines(['******************* End *******************\n\n'])



