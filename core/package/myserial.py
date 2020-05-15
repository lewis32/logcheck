#!/usr/bin/env Python
# coding=utf-8
import datetime
import threading
import time
# import serial
from serial import Serial
from serial.tools import list_ports
from .mylogging import MyLogging as Logging

log = Logging.getLogger(__name__)


class MySerial:
    def __init__(self, port=None, baudrate=115200, timeout=5):
        self.line_num = 1
        self.read_flag = True
        self.is_break = False

        self.serial = Serial(port, baudrate, timeout=timeout)
        self.serial.flushInput()
        self.serial.flushOutput()

    def open(self):
        self.serial.open()

    def close(self):
        self.serial.close()

    def is_open(self):
        return self.serial.isOpen()

    @staticmethod
    def get_port_list():
        port_list = list_ports.comports()
        return port_list

    def get_baudrate(self):
        return self.serial.baudrate

    def get_port(self):
        return self.serial.port

    def send_command(self, cmd):
        if self.is_open():
            self.serial.write((cmd + '\r\r').encode('utf-8'))
            time.sleep(1)

    def always_read_serial(self):
        while self.read_flag:
            value = self.serial.readline().decode('utf-8', errors="ignore")
            if not value:
                continue
            yield value

    def start_read_serial(self):
        self.read_flag = True
        t = threading.Thread(target=self.always_read_serial)
        t.start()
        time.sleep(1)

    def stop_read_serial(self):
        self.read_flag = False
