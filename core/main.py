from log_check import LogCheck
from my_serial import MySerial
from TV_serial import TVSerial


def main():
    # lc = LogCheck()
    # result = lc.check_log()
    serial = TVSerial('COM3')
    serial.sendComand('reboot')

if __name__ == '__main__':
    main()
