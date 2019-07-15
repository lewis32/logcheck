from log_check import LogCheck
from package.myserial import TVSerial
import time

def main():
    # lc = LogCheck()
    # result = lc.check_log()
    # serial = TVSerial('COM3')
    # serial.sendComand('reboot')

    s = TVSerial(port='COM3',baudrate=115200, timeout=5)
    s.startReadSerial()
    s.sendComand('\n\n')
    time.sleep(1)
    s.sendComand('log.off\n')
    time.sleep(1)
    s.sendComand('tail -f /var/local/logservice/logfile/tmp*\n')
    time.sleep(20)
    s.stopReadSerial()
    s.close()

if __name__ == '__main__':
    main()
