import os
import re
import json
import sys
import time
sys.path.append(os.path.abspath(os.getcwd()+'\\package'))
import myconfigparser

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
        # dirpath = os.getcwd()
        # filepath = os.path.join(dirpath,'policy.ini')
        # conf = configparser.ConfigParser()
        conf = myconfigparser.MyConfigParser()
        conf.read(self.filepath+r'\\conf\\policy.ini',encoding='utf-8')
        return conf

    def checkLog(self):
        loglist = self.loadLog()
        conf = self.loadPolicy()
        with open(self.filepath+r'\\result\\result-'+self.stime+'.txt','w') as f:
            for log in loglist:
                if log['EventCode'] not in conf.sections():
                    # print('Undefined EventCode:',log['EventCode'])
                    f.writelines(['Undefined EventCode:',log['EventCode'],'\n'])
                    # return 0
                for key in log:
                    if key not in conf.options('basic'):
                        if key not in conf.options(log['EventCode']):
                            f.writelines(['Undefined key:',key,'\n'])
                            continue
                        elif not re.match(eval(conf.get(log['EventCode'],key)),log[key]):
                            # f.writelines(['Passed key-value:',key,log[key],'\n'])
                        # else:
                            f.writelines(['Wrong key-value:',key,log[key],'\n'])
                    elif not re.match(eval(conf.get('basic',key)),log[key]):
                        # f.writelines(['Passed key-value:',key,log[key],'\n'])
                    # else:
                        f.writelines(['Wrong key-value:',key,log[key],'\n'])
                f.writelines(['*******************************\n'])
