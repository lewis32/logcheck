import json
import os
<<<<<<< HEAD
import myconfigparser

def loadLog():
    f = open('log.xml',encoding='utf-8')
    log = json.load(f)
    return log

def loadPolicy():
    dirpath = os.getcwd()
    filepath = os.path.join(dirpath,'basic.ini')
    # conf = configparser.ConfigParser()
    conf = myconfigparser.MyConfigParser()
    conf.read(filepath,encoding='utf-8')
    return conf

def checkLog():
    log = loadLog()
    conf = loadPolicy()
    if log['EventCode'] not in conf.sections():
        print('Undefined EventCode:',log['EventCode'])
        return 0
    for key in log:
        if key not in (conf.options('basic')+conf.options(log['EventCode'])):
            print('Undefined key:',key)
        # elif key not in conf.options(log['EventCode']):
        #     print('Undefined key:',key)
            continue
        if log[key] != conf.get(log['EventCode'],key):
            print('Undefined value:',log[key])
    #     if conf.get('basic','item') == log
    # for item in conf.options(log['EventCode']):


def main():
    checkLog()

if __name__ == '__main__':
    main()
=======
import re
import myconfigparser

class LogCheck(object):
    def loadLog(self):
        with open('log.xml','r+') as f:
            # start = f.read()
            # f.seek(0,0)
            # f.write('['+start)
            # f.seek(0,2)
            # f.write(']')
            # f.close()
            # log = json.load(f)
            text = f.read()
            if text.startswith('{'):
                text
        return log

    def loadPolicy(self):
        dirpath = os.getcwd()
        filepath = os.path.join(dirpath,'policy.ini')
        # conf = configparser.ConfigParser()
        conf = myconfigparser.MyConfigParser()
        conf.read(filepath,encoding='utf-8')
        return conf

    def checkLog(self,log,conf):
        # log = self.loadLog()
        # conf = self.loadPolicy()
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
>>>>>>> initial version
