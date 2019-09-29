import time
import os
import json
import sys
import re
from core.log_check import *
from core.package.myserial import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class logCheckUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('LogCheck')
        self.resize(500,300)

        mainLayout = QVBoxLayout()
        hboxLayout1 = QHBoxLayout()
        hboxLayout2 = QHBoxLayout()

        self.comboBox = QComboBox()
        self.comboBox.setCurrentIndex(-1)
        self.flushBtn = QPushButton('刷新串口')
        self.startBtn = QPushButton('开始')
        self.stopBtn = QPushButton('结束')

        self.comboBox.currentIndexChanged.connect(self.selectionChange)
        self.flushBtn.clicked.connect(lambda: self.flushBtnClick(self.flushBtn))
        self.startBtn.clicked.connect(lambda: self.startBtnClick(self.startBtn))
        self.stopBtn.clicked.connect(lambda: self.stopBtnClick(self.stopBtn))

        hboxLayout1.addWidget(self.comboBox)
        hboxLayout1.addWidget(self.flushBtn)
        mainLayout.addLayout(hboxLayout1)
        hboxLayout2.addWidget(self.startBtn)
        hboxLayout2.addWidget(self.stopBtn)
        mainLayout.addLayout(hboxLayout2)

        self.setLayout(mainLayout)

    def selectionChange(self,i):
        if self.comboBox.currentText():
            self.currentPort = re.findall(r'COM[0-9]+', self.comboBox.currentText())[0]
        print('Current Port: %s' % self.currentPort)

    def flushBtnClick(self,btn):
        self.comboBox.clear()
        self.port_list = getPortList()
        # self.comboBox.addItem('请选择通信端口')
        if self.port_list:
            for i in self.port_list:
                self.comboBox.addItem(str(i))

    def startBtnClick(self):
        self.s = TVSerial(port=self.currentPort, baudrate=115200, timeout=5)
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
        
    def stopBtnClick(self):
        self.flag = False  
        self.s.stopReadSerial()
        self.s.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = logCheckUI()
    main.show()
    sys.exit(app.exec_())
