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
        log_key = []
        conf_key = []
        log = list(log)
        conf = list(conf)
        conf.sort()
        for i in log:
            pos = bisect.bisect_left(conf,i)
            if pos < len(conf) and conf[pos].lower() == i.lower():
                mutual_key.append(i)
            elif pos >= len(conf):
                log_key.append(i)
        mutual_key = list(set(mutual_key))
        log_key = list(set(log_key))
        conf_key = list(set(conf).difference(set(mutual_key)))
        if len(log_key) != 0:
            f.writelines(['Undefined key-value: '])
            for i in log_key:
                f.writelines([i])
            f.writelines(['\n'])
        elif len(conf_key) != 0:
            f.writelines(['Lacking key-value: '])
            for i in conf_key:
                f.writelines([i,','])
            f.writelines(['\n'])
        # return mutual_key,log_key,conf_key

    def lowerKeys(self,key):
        return key.lower()

    def checkLog(self):
        loglist = self.loadLog()
        conflist = self.loadPolicy()
        with open(self.filepath+r'\\result\\result-'+self.stime+'.txt','w',encoding='utf-8' ) as f:
            '''
            for log in loglist:
                for kw in log:
                    if kw.lower() != 'eventcode':
                        f.writelines(['Lacking key: EventCode'])
                    elif log[kw] not in conf.sections():
                        f.writelines(['Undefined EventCode:',log['EventCode'],'\n'])
                    else:
                        mutual_key,log_key,conf_key = self.compareKeys(log,conf.options('common')+conf.options(log[kw]))
                        if len(log_key) != 0:
                            f.writelines(['Undefined key-value: '])
                            for i in log_key:
                                f.writelines([i])
                            f.writelines(['\n'])
                        elif len(conf_key) != 0:
                            f.writelines(['Lacking key-value: '])
                            for i in conf_key:
                                f.writelines([i])
                            f.writelines(['\n'])
                    for key in log:
                        if key not in conf.options('common'):
                            if key not in conf.options(kw):
                                # f.writelines(['Undefined key:',key,'\n'])
                                continue
                            elif not re.match(eval(conf.get(kw,key)),log[key]):
                                f.writelines(['Wrong key-value: ',key,':',log[key],'\n'])
                        elif not re.match(eval(conf.get('common',key)),log[key]):
                            f.writelines(['Wrong key-value: ',key,':',log[key],'\n'])
                    f.writelines(['\n******************* NEXT LOG *******************\n\n'])
            '''
            for log in loglist:
                count = len(log)
                n = 1
                for key in log:
                    print(self.lowerKeys(key))
                    if self.lowerKeys(key) != 'eventcode' and n < count:
                        n += 1
                        print(n)
                        continue
                    elif self.lowerKeys(key) != 'eventcode' and n == count:
                        f.writelines(['\nCouldn\'t find the key eventcode\n'])
                        break
                    else:
                        conf = dict(conflist.items(log[key]) + conflist.items('common'))
                        for i in conf:
                            conf[self.lowerKeys(i)] = conf.pop(i)
                        print(conf)
                        print(log)
                        self.compareKeys(log,conf,f)
                        for key in log:
                            if self.lowerKeys(key) not in conf:
                                f.writelines(['Undefined key:',key,'\n'])
                                continue
                            try:
                                print(eval(conf[self.lowerKeys(key)]),log[key])
                                if not re.match(eval(conf[self.lowerKeys(key)]),log[key]):
                                    f.writelines(['Wrong key-value: ',key,':',log[key],'\n'])
                            except Exception as e:
                                print(e)
                            finally:
                                f.writelines(['\n******************* NEXT LOG *******************\n\n'])
                                break


