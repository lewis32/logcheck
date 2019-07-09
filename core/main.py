from log_check import LogCheck
from my_serial import MySerial
from TV_serial import TVSerial
import serial

def main():
    # lc = LogCheck()
    # result = lc.check_log()
    # serial = TVSerial('COM3')
    # serial.sendComand('reboot')

    s = serial.Serial(port='COM3',baudrate=115200, timeout=5)
    s.flushInput()
    s.flushOutput()
    print(s.portstr)
    # s.write('\n\n'.encode('utf-8'))
    s.write('\n\nreboot\n'.encode('utf-8'))

if __name__ == '__main__':
    main()
