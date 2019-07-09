#!/usr/bin/env Python
# coding=utf-8
import datetime
import threading
import time
import sys
import os
# import serial
import my_serial

class TVSerial(my_serial.MySerial):
    lineNo = 1
    currentTime = time.strftime('%Y%m%d-%H%M%S', time.localtime())
    filename = 'serialLog-%s.log' % currentTime
    filepath = os.path.join(sys.path[0], 'serial_log', filename)
    if not os.path.exists(os.path.dirname(filepath)):
        os.mkdir(os.path.dirname(filepath))
    f = open(filepath, "w",encoding='utf-8')
    read_flag=True
    isBreak = False

    # def __init__(self, port, baud_rate=115200, timeout=5):
    #     # self.s = serial.Serial(port, baud_rate, timeout)
    #     super(my_serial.MySerial, self).__init__(port, baud_rate, timeout)

    def setLogPath(self,newPath):
        if (newPath=='') or (newPath==None):
            # self.logger.error('newPath为空')
            return
        self.f.close()
        self.filename=newPath
        self.f = open(self.filename, "w",encoding='utf-8')

    def sendComand(self,cmd):
        # self.logger.info('发送串口命令：'+cmd)
        if(not(self.isOpen())):
            self.open()
        self.s.write(cmd.encode('utf-8'))

    #一直读串口打印
    def alwayseReadSerial(self):
        # self.logger.info('串口开始打印')

        while (self.read_flag):
            value=self.s.readline().decode('utf-8',errors="ignore")
            if(""==value or None==value):
                continue
            data ="["+time.strftime('%Y%m%d-%H%M%S', time.localtime())+"]"+" "+value
            self.f.write(data)
            self.lineNo=self.lineNo+1
            # print(data)
            self.f.flush()
        if(not self.read_flag):
            self.f.close()

    #开始打印
    def startReadSerial(self):
        currentTime = time.strftime('%Y%m%d-%H%M%S', time.localtime())
        newFile=sys.path[0]+'/serialLog/' + currentTime + '.log' # Linux
        # newFile=sys.path[0]+'\\serialLog\\' + currentTime + '.log' # Windows
        self.setLogPath(newFile)
        self.read_flag = True
        t = threading.Thread(target=self.alwayseReadSerial)
        t.start()
        time.sleep(1)

    #停止打印
    def stopReadSerial(self):
        self.read_flag = False

    def send(self, cmd):
        self.s.write(cmd.encode('utf-8'))

    def get_last_line(self,inputfile,num) :
        dat_file = open(inputfile, 'r',encoding='utf-8')
        lines = dat_file.readlines()
        count = len(lines)
        if count<num:
            num=count
            i=1
        lastre = []
        for i in range(1,(num+1)):
            if lines:
                n = -i
                last_line = lines[n].strip()
                dat_file.close()
                lastre.append(last_line)
        return lastre

    #过滤文件最后几行是否存在某字符串
    def waitForString(self,keyWord,timeout):
        starttime = datetime.datetime.now()
        while True:
            print(str(timeout))
            re = self.get_last_line(self.filename,30)
            currenttime = datetime.datetime.now()
            interval = (currenttime - starttime).seconds
            # print("interval=="+str(interval))
            if interval > timeout:
                return ""
            for n in re:
                if n.find(keyWord)>=0:
                    print(('pass',n))
                    return n

#####################  电视机串口测试代码 #######################
if __name__=='__main__':
    s=TVSerial('com1')
    s.startReadSerial()
    s.sendComand("1969 \n")
    time.sleep(1)
    s.sendComand("1969 \n")
    time.sleep(1)

    # time.sleep(5)
    # s.sendComand("sh /data/local/tmp/test.sh \n")

    s.sendComand("reboot \n")
    s.waitForString( "Starting kernel",5)

    # s.sendComand("ping -c 4 -W 1 10.18.203.235 \n")
    # s.waitForString(s.filename, "transmitted",10)
    s.stopReadSerial()
    s.close()
    print("end")
