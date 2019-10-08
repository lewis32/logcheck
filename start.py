# pylint: disable-msg=invalid-name,global-statement

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
    ''' child thread '''
    add = pyqtSignal(dict)
    terminal = pyqtSignal(object)

    def run(self):
        global portList, currentPort, isStarted

        if not portList or not currentPort:
            return
        try:
            self.serial = TVSerial(port=currentPort, baudrate=115200, timeout=5)
        except Exception as e:
            self.terminal.emit(e)
        else:
            self.serial.sendComand('\n\nlog.off\n')
            self.sleep(1)
            self.serial.sendComand('tail -f /var/local/logservice/logfile/tmp*\n')
            self.serial.startReadSerial()
            isStarted = True
            self.serial.s.flushInput()
            self.serial.s.flushOutput()
            
            self.lc = LogCheck()
            while True:
                if not isStarted:
                    self.terminal.emit('正常结束！')
                    break
                # self.sleep(1)
                block = self.serial.s.readline().decode('utf-8', errors='ignore')
                if block and block != '\n':
                    ret = self.lc.check_log(block)
                    ret = json.dumps(ret, ensure_ascii=False, indent=4)
                    self.add.emit(ret)
                    print('test11111111111111111')
                # self.add.emit()
                newDict = {
                    'src_event_code': 100000,
                    'event_code': 100001,
                    'missing_key': ['xxxxxx', 'yyyyyy'],
                    'undefined_key': {'xxxx': 'testing'},
                    'invalid_key': {'yyyyy': 'testing'},
                    'result': 0
                    }
                self.add.emit(newDict)
                print('test000000000000')


class LogCheckUI(QWidget):
    ''' UI main thread '''
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        '''initiates application UI'''
        self.setWindowTitle('LogCheck')
        self.resize(500, 300)

        mainLayout = QVBoxLayout()
        hboxLayout1 = QHBoxLayout()
        hboxLayout2 = QHBoxLayout()

        self.comboBox = QComboBox()
        self.comboBox.setCurrentIndex(-1)
        self.flushBtn = QPushButton('刷新串口')

        self.table = QTableWidget(1, 6)
        self.table.setHorizontalHeaderLabels(['上级事件码', '本级事件码', '是否通过', '缺少字段', '错误字段', '多余字段'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # self.row = 0

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
        global currentPort

        if self.comboBox.currentText():
            currentPort = re.findall(r'COM[0-9]+', self.comboBox.currentText())[0]
        print('Current Port: %s' % currentPort)
 
    def flushBtnClick(self, btn):
        global portList

        self.comboBox.clear()
        portList = getPortList()
        if portList:
            for i in portList:
                self.comboBox.addItem(str(i))
        self.comboBox.setCurrentIndex(-1)

    def startBtnClick(self, btn):
        global currentPort, isStarted

        if not currentPort:
            QMessageBox.information(self, '提示', '请选择当前端口', QMessageBox.Ok)
            return
        self.table.clearContents()
        self.row = 0
        self.table.setRowCount(self.row + 1)
        self.workThread.start()
        isStarted = True
        print('startBtnClick: row is %s' % self.row)
        
    def stopBtnClick(self, btn):
        global isStarted

        if not isStarted:
            return
        isStarted = False
        # self.row = -1
        self.workThread.serial.stopReadSerial()
        self.workThread.serial.close()
        print('stopBtnClick: row is %s' % self.row)

    def addText(self, result):
        '''add check result'''
        print('test addText')
        self.table.setItem(self.row, 0, QTableWidgetItem(str(self.row) + str(result['src_event_code'])))
        self.table.setItem(self.row, 1, QTableWidgetItem(str(result['event_code'])))
        self.table.setItem(self.row, 2, QTableWidgetItem('不通过' if result['result'] else '通过'))
        self.table.setItem(self.row, 3, QTableWidgetItem(str(result['missing_key'])))
        self.table.setItem(self.row, 4, QTableWidgetItem(str(result['invalid_key'])))
        self.table.setItem(self.row, 5, QTableWidgetItem(str(result['undefined_key'])))
        self.row += 1
        self.table.setRowCount(self.row + 1)
        print('addText: row is %s' % self.row)

    def terminalText(self, text):
        '''pause check'''
        QMessageBox.information(self, '提示', str(text), QMessageBox.Ok)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = LogCheckUI()
    main.show()
    sys.exit(app.exec_())
