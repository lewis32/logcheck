import os
import re
import json
import sys
import time
import bisect
# sys.path.append(os.path.abspath(os.getcwd()+'\\package'))
import package.myconfigparser

class LogCheck():
    filepath = os.path.abspath((os.path.dirname(os.getcwd())))
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

    def compareKey(self):
        loglist = self.loadLog()
        conf = self.loadPolicy()
        with open(self.filepath+r'\\result\\result-'+self.stime+'.txt','w') as f:
            samedatalist = []
            for log in loglist:
                samedata = []
                exlogdata = []
                exconfdata = []
                log = list(log)
                for i in log:
                    pos = bisect.bisect_left(conf,i)
                    if pos < len(conf) and conf[pos] == i:
                        samedata.append(i)
                    elif pos >= len(conf):
                        exlogdata.append(i)
                samedata = list(set(samedata))
                print(samedata)




    def checkLog(self):
        loglist = self.loadLog()
        conf = self.loadPolicy()
        with open(self.filepath+r'\\result\\result-'+self.stime+'.txt','w') as f:
            for log in loglist:
                if log['EventCode'] not in conf.sections():
                    f.writelines(['Undefined EventCode:',log['EventCode'],'\n'])
                for key in log:
                    if key not in conf.options('basic'):
                        if key not in conf.options(log['EventCode']):
                            f.writelines(['Undefined key:',key,'\n'])
                            continue
                        elif not re.match(eval(conf.get(log['EventCode'],key)),log[key]):
                            f.writelines(['Wrong key-value:',key,log[key],'\n'])
                    elif not re.match(eval(conf.get('basic',key)),log[key]):
                        f.writelines(['Wrong key-value:',key,log[key],'\n'])
                f.writelines(['*******************************\n'])
