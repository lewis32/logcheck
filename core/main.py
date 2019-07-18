from log_check import LogCheck
from package.myserial import TVSerial
import time
import os
import json

def main():
    s = TVSerial(port='COM3',baudrate=115200, timeout=5)
    s.sendComand('\n\n')
    time.sleep(1)
    s.sendComand('log.off\n')
    time.sleep(1)
    s.sendComand('tail -f /var/local/logservice/logfile/tmp*\n')
    s.startReadSerial()
    s.s.flushInput()
    s.s.flushOutput()
    lc = LogCheck(has_data=True)
    LOOP = 20
    count = 0
    while True:
        if count == LOOP:
            break
        block = s.s.readline().decode('utf-8', errors='ignore')
        if block != '' and block != '\n' and block is not None:
            ret = lc.check_log(block)
            ret_json = json.dumps(ret, ensure_ascii=False, indent=4)
            print(ret_json)
            time.sleep(0.01)
            count += 1
    s.stopReadSerial()
    s.close()

if __name__ == '__main__':
    main()
