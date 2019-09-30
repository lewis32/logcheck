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

isStarted = False
portList = []
currentPort = None
logText = 'This is default string'


class WorkThread(QThread):
    add = pyqtSignal()
    terminal = pyqtSignal()

    def run(self):
        print('test begin')
        global portList, currentPort, isStarted
        if not portList or not currentPort:
            return
        try:
            self.serial = TVSerial(port=currentPort, baudrate=115200, timeout=5)
        except Exception as e:
            self.terminal.emit()
            print(e)
        else:
            self.serial.sendComand('\n\nlog.off\n')
            self.sleep(1)
            self.serial.sendComand('tail -f /var/local/logservice/logfile/tmp*\n')
            self.serial.startReadSerial()
            self.serial.s.flushInput()
            self.serial.s.flushOutput()
            while True:
                if not isStarted:
                    self.terminal.emit()
                    break
                # self.sleep(1)
                block = self.serial.s.readline().decode('utf-8', errors='ignore')
                if block and block != '\n':
                    ret = lc.check_log(block)
                    ret = json.dumps(ret, ensure_ascii=False, indent=4)
                    global logText
                    logText = str(ret)
                    self.add.emit()
                    print('test11111111111111111')
                # self.add.emit()
                print('test000000000000')


class LogCheckUI(QWidget):
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

        self.table = QTableWidget(20, 4)
        self.table.setHorizontalHeaderLabels(['srceventcode', 'eventcode', '是否通过', '详细信息'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.row = 0

        self.startBtn = QPushButton('开始')
        self.stopBtn = QPushButton('结束')
        self.workThread = WorkThread()

        self.comboBox.currentIndexChanged.connect(self.selectionChange)
        self.flushBtn.clicked.connect(lambda: self.flushBtnClick(self.flushBtn))
        # self.startBtn.clicked.connect(lambda: self.startBtnClick(self.startBtn))
        self.stopBtn.clicked.connect(lambda: self.stopBtnClick(self.stopBtn))
        self.workThread.add.connect(self.addText)
        self.workThread.terminal.connect(self.terminalText)
        self.startBtn.clicked.connect(self.startBtnClick)

        hboxLayout1.addWidget(self.comboBox)
        hboxLayout1.addWidget(self.flushBtn)
        mainLayout.addLayout(hboxLayout1)
        mainLayout.addWidget(self.table)
        hboxLayout2.addWidget(self.startBtn)
        hboxLayout2.addWidget(self.stopBtn)
        mainLayout.addLayout(hboxLayout2)

        self.setLayout(mainLayout)

    def selectionChange(self, i):
        if self.comboBox.currentText():
            global currentPort
            currentPort = re.findall(r'COM[0-9]+', self.comboBox.currentText())[0]
        print('Current Port: %s' % currentPort)

    def flushBtnClick(self, btn):
        self.comboBox.clear()
        global portList
        portList = getPortList()
        if portList:
            for i in portList:
                self.comboBox.addItem(str(i))
        self.comboBox.setCurrentIndex(-1)

    def startBtnClick(self, btn):
        self.table.clearContents()
        self.workThread.start()
        global isStarted
        isStarted = True
        print('startBtnClick: row is %s' % self.row)
        
    def stopBtnClick(self, btn):
        global isStarted
        isStarted = False
        self.row = -1
        self.workThread.serial.stopReadSerial()
        self.workThread.serial.close()
        print('stopBtnClick: row is %s' % self.row)

    def addText(self):
        print('test addText')
        global logText
        self.table.setItem(self.row, 0, QTableWidgetItem(logText))
        self.row += 1
        print('addText: row is %s' % self.row)

    def terminalText(self):
        print('test terminalText')
        QMessageBox.information(self, '消息', '结束', QMessageBox.Ok)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = LogCheckUI()
    main.show()
    sys.exit(app.exec_())
