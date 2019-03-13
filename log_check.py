import json
import os
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
