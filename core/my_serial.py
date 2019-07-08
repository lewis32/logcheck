#!/usr/bin/env python
# -*- coding: utf-8 -*-
import serial


class MySerial(object):

##单例模式：python可以通过__new__来实现单例模式。
## __new__原型为object.__new__(cls,[...]),cls是一个类对象。当你调用C(*arg, **kargs)来创建一个类C的实例时。
# python内部调用是C.__new__(C, *arg, **kargs),然后返回值是类C的实例c。
# 在确认c是C的实例后，python再调用C.__init__(c, *arg, **kargs)来实例化c。
#单例模式创建的对象完全相同,可以用id(), ==, is检测
#is_first：是否是首个对象的标志位
    is_first = False

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, port, baud_rate=115200, timeout=5):
        # if (serialport.is_first == True):
        self.s = serial.Serial(port, baud_rate, timeout)
        self.s.flushInput()
        self.s.flushOutput()

    def sendComand(self,cmd):
        if(not(self.isOpen())):
            self.open()
        self.s.write(cmd)

    def close(self):
        self.s.close()

    def isOpen(self):
        return self.s.isOpen()

    def open(self):
        self.s.open()

    def setBaudrate(self,newBaudrate):
        self.s.baudrate=newBaudrate

    def getBaudrate(self):
        return self.s.baudrate

    def getPortname(self):
        return self.s.port


############## 串口遥控器测试代码 ###########
if __name__=='__main__':
    pass
    # ir=serialport('com9')
    # print(ir.isOpen())
    # ir.sendComand('muji \n')
    # ir.sendComand('muji \n')
    # ir.sendComand('reboot \n')
    # print(ir.getPortname())
    # print(ir.getBaudrate())
    # ir.close()
