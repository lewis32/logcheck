import time
import os
import json
import sys
from core.log_check import LogCheck
from core.package.myserial import TVSerial
from core.Ui_demo import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QDialog

class new_mainwindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def on_btn_start_clicked(self):
        self.s = TVSerial(port='COM3',baudrate=115200, timeout=5)
        self.s.sendComand('\n\n')
        time.sleep(1)
        self.s.sendComand('log.off\n')
        time.sleep(1)
        self.s.sendComand('tail -f /var/local/logservice/logfile/tmp*\n')
        self.s.startReadSerial()
        self.s.s.flushInput()
        self.s.s.flushOutput()
        lc = LogCheck(has_data=True)
        self.flag = True
        # while self.flag:
        for i in range(5):
            block = self.s.s.readline().decode('utf-8', errors='ignore')
            if block != '' and block != '\n' and block is not None:
                ret = lc.check_log(block)
                ret_json = json.dumps(ret, ensure_ascii=False, indent=4)
                
                time.sleep(0.01)
        
    def on_btn_stop_clicked(self):
        self.flag = False
        self.s.stopReadSerial()
        self.s.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = new_mainwindow()
    window.show()
    sys.exit(app.exec_())