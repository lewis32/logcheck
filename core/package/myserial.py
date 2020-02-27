#!/usr/bin/env Python
# coding=utf-8
import datetime
import threading
import time
import sys
import os
import serial
from serial.tools import list_ports
from .mylogging import MyLogging as Logging


def getPortList():
    port_list = list(list_ports.comports())
    if len(port_list) == 0:
        return
    else:
        return port_list


class TVSerial():
    lineNo = 1
    # currentTime = time.strftime('%Y%m%d-%H%M%S', time.localtime())
    # filename = 'SerialLog-%s.log' % currentTime
    # filepath = os.path.join(os.path.dirname(sys.path[0]), 'log', filename)
    # if not os.path.exists(os.path.dirname(filepath)):
    #     os.mkdir(os.path.dirname(filepath))
    # f = open(filepath, "w", encoding='utf-8')
    read_flag = True
    isBreak = False

    # def __new__(cls, *args, **kwargs):
    #     if not hasattr(cls, '_instance'):
    #         cls._instance = super().__new__(cls)
    #     return cls._instance

    def __init__(self, port='COM3', baudrate=115200, timeout=5):
        self.logger = Logging()
        self.s = serial.Serial(port, baudrate, timeout=timeout)
        self.s.flushInput()
        self.s.flushOutput()

    def close(self):
        self.s.close()

    def isOpen(self):
        return self.s.isOpen()

    def open(self):
        self.s.open()

    def setBaudrate(self, newBaudrate):
        self.s.baudrate = newBaudrate

    def getBaudrate(self):
        return self.s.baudrate

    def getPortname(self):
        return self.s.port

    def setLogPath(self, newPath):
        if newPath == '' or newPath is None:
            # self.logger.error('newPath为空')
            return
        self.f.close()
        self.filename = newPath
        self.f = open(self.filename, "w", encoding='utf-8')

    def sendComand(self, cmd):
        # self.logger.info('发送串口命令：'+cmd)
        if not (self.isOpen()):
            self.open()
        self.s.write(cmd.encode('utf-8'))

    # 一直读串口打印
    # def alwayseReadSerial(self):
    #     while (self.read_flag):
    #         value=self.s.readline().decode('utf-8',errors="ignore")
    #         if(value == '' or value is None):
    #             continue
    #         self.f.write(value)
    #         self.lineNo = self.lineNo + 1
    #         self.f.flush()
    #     if(not self.read_flag):
    #         self.f.close()

    def alwayseReadSerial(self):
        while self.read_flag:
            value = self.s.readline().decode('utf-8', errors="ignore")
            if value == '' or value is None:
                continue
            yield value

    # 开始打印
    def startReadSerial(self):
        # currentTime = time.strftime('%Y%m%d-%H%M%S', time.localtime())
        # newFile = os.path.join(sys.path[0], 'serial_log', '%s.log' % currentTime)
        # self.setLogPath(self.filepath)
        self.read_flag = True
        t = threading.Thread(target=self.alwayseReadSerial)
        t.start()
        time.sleep(1)

    # 停止打印
    def stopReadSerial(self):
        self.read_flag = False

    def get_last_line(self, inputfile, num):
        dat_file = open(inputfile, 'r', encoding='utf-8')
        lines = dat_file.readlines()
        count = len(lines)
        if count < num:
            num = count
            i = 1
        lastre = []
        for i in range(1, (num + 1)):
            if lines:
                n = -i
                last_line = lines[n].strip()
                dat_file.close()
                lastre.append(last_line)
        return lastre

    # 过滤文件最后几行是否存在某字符串
    def waitForString(self, keyWord, timeout):
        starttime = datetime.datetime.now()
        while True:
            self.logger.info("Timeout: " + str(timeout))
            re = self.get_last_line(self.filepath, 30)
            currenttime = datetime.datetime.now()
            interval = (currenttime - starttime).seconds
            # print("interval=="+str(interval))
            if interval > timeout:
                return ""
            for n in re:
                if n.find(keyWord) >= 0:
                    self.logger.info("Get the keyword successfully! " + n)
                    return n


if __name__ == '__main__':
    s = TVSerial('COM3')
    s.startReadSerial()
    s.sendComand("\n\n")
    time.sleep(1)

    s.sendComand("reboot \n")
    s.waitForString("Starting kernel", 5)

    s.stopReadSerial()
    s.close()
    s.logger.info("Now your serial is disconnected!")
