from log_check import LogCheck
from package.myserial import TVSerial
import time
import os

def main():
    lc = LogCheck()
    # result = lc.check_log()
    # serial = TVSerial('COM3')
    # serial.sendComand('reboot')

    s = TVSerial(port='COM3',baudrate=115200, timeout=5)
    s.sendComand('\n\n')
    time.sleep(1)
    s.sendComand('log.off\n')
    time.sleep(1)
    s.sendComand('tail -f /var/local/logservice/logfile/tmp*\n')
    s.startReadSerial()
    with open(s.filepath) as f:
        size = 0
        # while True:
        for i in range(10):
            time.sleep(1)
            new_size = os.path.getsize(s.filepath)
            if size != new_size:
                size = new_size
                print(size)
                block = s.s.readline().decode('utf-8', errors='ignore')
                f.flush()
                # block = f.readline()
                print(block.__repr__())
                if block != '' and block is not None:
                    print(111111)
                    print(block)
                    # ret = lc.check_log()
                    # print(ret)
    s.stopReadSerial()
    s.close()

if __name__ == '__main__':
    main()
