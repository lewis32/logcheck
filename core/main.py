from log_check import LogCheck
from package.myserial import TVSerial
import time
import os

def main():
    s = TVSerial(port='COM3',baudrate=115200, timeout=5)
    s.sendComand('\n\n')
    time.sleep(1)
    s.sendComand('log.off\n')
    time.sleep(1)
    s.sendComand('tail -f /var/local/logservice/logfile/tmp*\n')
    s.startReadSerial()
    lc = LogCheck(has_data=True)
    # size = 0
    # print(size)
    LOOP = 20
    count = 0
    while True:
        # new_size = os.path.getsize(s.filepath)
        # if size != new_size:
        #     size = new_size
        #     print(size)
        #     block = s.s.readline().decode('utf-8', errors='ignore')
        #     print(block.__repr__())
        #     if block != '' and block is not None:
        #         print(111111)
        #         print(block)
        #         ret = lc.check_log(block)
        #         print(ret)
        if count == LOOP:
            break
        block = s.s.readline().decode('utf-8', errors='ignore')
        if block != '' and block != '\n' and block is not None:
            print(block.__repr__())
            ret = lc.check_log(block)
            print(type(ret))
            time.sleep(0.01)
            count += 1
    s.stopReadSerial()
    s.close()

if __name__ == '__main__':
    main()
