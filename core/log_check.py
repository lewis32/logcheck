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

    def compareKeys(self,log,conf):
        mutual_key = []
        ex_key_log = []
        ex_key_conf = []
        log = list(log)
        conf = list(conf)
        conf.sort()
        for i in log:
            pos = bisect.bisect_left(conf,i)
            print(pos,len(conf))
            if pos < len(conf) and conf[pos] == i:
                mutual_key.append(i)
            elif pos >= len(conf):
                ex_key_log.append(i)
        mutual_key = list(set(mutual_key))
        ex_key_log = list(set(ex_key_log))
        ex_key_conf = list(set(conf).difference(set(mutual_key)))
        return mutual_key,ex_key_log,ex_key_conf

    def checkLog(self):
        loglist = self.loadLog()
        conf = self.loadPolicy()
        with open(self.filepath+r'\\result\\result-'+self.stime+'.txt','w',encoding='utf-8' ) as f:
            for log in loglist:
                if log['EventCode'] not in conf.sections():
                    f.writelines(['Undefined EventCode:',log['EventCode'],'\n'])
                else:
                    mutual_key,ex_key_log,ex_key_conf = self.compareKeys(log,conf.options('basic')+conf.options(log['EventCode']))
                    if len(ex_key_log) != 0:
                        f.writelines(['Undefined key-value: '])
                        for i in ex_key_log:
                            f.writelines([i])
                        f.writelines(['\n'])
                    elif len(ex_key_conf) != 0:
                        f.writelines(['Lacking key-value: '])
                        for i in ex_key_conf:
                            f.writelines([i])
                        f.writelines(['\n'])
                    else:
                        f.writelines(['log keys is the same as conf keys'])
                for key in log:
                    if key not in conf.options('basic'):
                        if key not in conf.options(log['EventCode']):
                            # f.writelines(['Undefined key:',key,'\n'])
                            continue
                        elif not re.match(eval(conf.get(log['EventCode'],key)),log[key]):
                            f.writelines(['Wrong key-value: ',key,':',log[key],'\n'])
                    elif not re.match(eval(conf.get('basic',key)),log[key]):
                        f.writelines(['Wrong key-value: ',key,':',log[key],'\n'])
                f.writelines(['*******************下一条日志*******************\n'])
