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

    def compareKeys(self,log,conf,f):
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
        if len(log_key) != 0:
            f.writelines(['日志存在多余key: '])
            for i in log_key:
                f.writelines([i,','])
            f.writelines(['\n'])
        if len(conf_key) != 0:
            f.writelines(['日志存在缺少key: '])
            for i in conf_key:
                f.writelines([i,','])
            f.writelines(['\n'])
        return mutual_key

    def lowerKeys(self,key):
        return key.lower()

    def compareTimestamp(self,log):
        st = 1
        et = 2
        for key in log:
            if self.lowerKeys(key) == 'starttime':
                st = log[key]
            if self.lowerKeys(key) == 'endtime':
                et = log[key]
        if st == 0:
            f.writelines(['starttime is equal to zero'])
        if st != 0 and et != 0 and st >= et:
            f.writelines(['starttime is NOT greater than endtime'])

    def checkLog(self):
        try:
            loglist = self.loadLog()
        except Exception as e:
            print("日志存在格式不规范: ",e)

        try:
            conflist = self.loadPolicy()
        except Exception as e:
            print("策略存在格式不规范: ",e)

        with open(self.filepath+r'\\result\\result-'+self.stime+'.txt','w',encoding='utf-8' ) as f:
            for log in loglist:
                count = len(log)
                n = 1
                for key in log:
                    if self.lowerKeys(key) != 'eventcode' and n < count:
                        n += 1
                        continue
                    elif self.lowerKeys(key) != 'eventcode' and n == count:
                        f.writelines(['\nCouldn\'t find the key eventcode\n'])
                        break
                    else:
                        try:
                            conf = dict(conflist.items(log[key]) + conflist.items('common'))
                        except Exception as e:
                            print("日志存在eventcode不规范: ",e)

                        for i in conf:
                            conf[self.lowerKeys(i)] = conf.pop(i)
                        print(conf)
                        print(log)
                        mutual_key = self.compareKeys(log,conf,f)
                        mutual_dict = {}
                        for i in mutual_key:
                            mutual_dict[i] = conf[self.lowerKeys(i)]
                        for key in mutual_dict:
                            if not re.match(eval(mutual_dict[key]),str(log[key])):
                                f.writelines(['Wrong key-value: ',key,':',log[key],'\n'])
                f.writelines(['\n******************* NEXT LOG *******************\n\n'])



