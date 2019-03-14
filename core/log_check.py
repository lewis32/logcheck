import os
import re
import json
import sys
sys.path.append(os.getcwd()+'\\package')

import myconfigparser

class LogCheck():
    def loadLog(self):
        filepath = os.path.abspath(os.path.dirname(os.getcwd()))
        with open(filepath+'\\conf\\log.xml','r+') as f:
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
        filepath = os.path.abspath(os.path.dirname(os.getcwd()))
        # conf = configparser.ConfigParser()
        conf = myconfigparser.MyConfigParser()
        conf.read(filepath+'\\conf\\policy.ini',encoding='utf-8')
        return conf

    def checkLog(self):
        loglist = self.loadLog()
        conf = self.loadPolicy()
        for log in loglist:
            if log['EventCode'] not in conf.sections():
                print('Undefined EventCode:',log['EventCode'])
                return 0
            for key in log:
                if key not in conf.options('basic'):
                    if key not in conf.options(log['EventCode']):
                        print('Undefined key:',key)
                        continue
                    elif re.match(eval(conf.get(log['EventCode'],key)),log[key]):
                        print('Passed key-value:',key,log[key])
                    else:
                        print('Wrong key-value:',key,log[key])
                elif re.match(eval(conf.get('basic',key)),log[key]):
                    print('Passed key-value:',key,log[key])
                else:
                    print('Wrong key-value:',key,log[key])
            print('**********************************')
