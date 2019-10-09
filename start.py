# pylint: disable-msg=invalid-name,global-statement

import time
import os
import json
import sys
import re
import collections
from core.log_check import *
from core.package.myserial import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

isStarted = False
portList = []
currentPort = None
# logText = 'This is default string'


class WorkThread(QThread):
    """
    Child thread
    """

    add = pyqtSignal(list, list)
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
                newDict = [
                    {
                        'src_event_code': 100000,
                        'event_code': 100001,
                        'missing_key': ['xxxxxx', 'yyyyyy'],
                        'invalid_key': {'yyyyy': 'testing'},
                        'undefined_key': {'xxxx': 'testing'},
                        'result': 0
                    },
                    {
                        'src_event_code': None,
                        'event_code': None,
                        'missing_key': ['xxxxxx', 'yyyyyy'],
                        'invalid_key': {'yyyyy': 'testing'},
                        'undefined_key': {'xxxx': 'testing'},
                        'result': 1
                    }
                ]
                self.add.emit(newDict, newDict)
                print('test000000000000')


class LogCheckUI(QWidget):
    """
    UI main thread
    """

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """initiates application UI"""
        self.setWindowTitle('LogCheck')
        self.resize(900, 450)

        mainLayout = QVBoxLayout()
        hboxLayoutHead = QHBoxLayout()
        hboxLayoutFooter = QHBoxLayout()
        hboxLayoutBody = QHBoxLayout()

        self.comboBox = QComboBox()
        self.comboBox.setCurrentIndex(-1)
        self.flushBtn = QPushButton('刷新串口')

        self.table = QTableWidget(1, 5)
        font = QFont()
        font.setPointSize(10)
        self.table.setFont(font)
        self.table.setHorizontalHeaderLabels(['上级事件码', '本级事件码', '是否通过', '原始数据', '结果详情'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setColumnHidden(3, True)
        self.table.setColumnHidden(4, True)
        # self.row = 0

        self.textEditData = QTextEdit()
        self.textEditData.setReadOnly(True)
        self.textEditData.setFontPointSize(10)
        self.textEditRes = QTextEdit()
        self.textEditRes.setReadOnly(True)
        self.textEditRes.setFontPointSize(10)

        self.startBtn = QPushButton('开始')
        self.stopBtn = QPushButton('结束')
        self.workThread = WorkThread()

        self.comboBox.currentIndexChanged.connect(self.selectionChange)
        self.flushBtn.clicked.connect(lambda: self.flushBtnClick(self.flushBtn))
        # self.startBtn.clicked.connect(lambda: self.startBtnClick(self.startBtn))
        self.stopBtn.clicked.connect(lambda: self.stopBtnClick(self.stopBtn))
        # self.table.itemClicked.connect(self.itemClick)
        self.table.cellClicked.connect(self.itemClick)
        self.workThread.add.connect(self.addText)
        self.workThread.terminal.connect(self.terminalText)
        self.startBtn.clicked.connect(self.startBtnClick)

        hboxLayoutHead.addWidget(self.comboBox)
        hboxLayoutHead.addWidget(self.flushBtn)
        mainLayout.addLayout(hboxLayoutHead)
        hboxLayoutBody.addWidget(self.table)
        hboxLayoutBody.addWidget(self.textEditData)
        hboxLayoutBody.addWidget(self.textEditRes)
        mainLayout.addLayout(hboxLayoutBody)
        hboxLayoutFooter.addWidget(self.startBtn)
        hboxLayoutFooter.addWidget(self.stopBtn)
        mainLayout.addLayout(hboxLayoutFooter)

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

    def addText(self, data, res):
        """
        add check result
        """
        print('test addText')
        cnt = 0
        for i in res:
            self.table.setItem(self.row, 0, QTableWidgetItem(str(i['src_event_code'])))
            self.table.setItem(self.row, 1, QTableWidgetItem(str(i['event_code'])))
            if i['result']:
                item = QTableWidgetItem('不通过')
                # item.setBackground(Union[QColor(60, 60, 10)])
            else:
                item = QTableWidgetItem('通过')
            self.table.setItem(self.row, 2, item)
            # self.table.setItem(self.row, 2, QTableWidgetItem('不通过' if res['result'] else '通过'))
            self.table.setItem(self.row, 3, QTableWidgetItem(json.dumps(data[cnt], indent=4)))
            self.table.setItem(self.row, 4, QTableWidgetItem(json.dumps(i, indent=4)))

            cnt += 1
            self.row += 1
            self.table.setRowCount(self.row + 1)
            print('addText: row is %s' % self.row)

    def itemClick(self, row):
        """
        click item and display detail info"""
        if self.table.item(row, 3) and self.table.item(row, 4):
            self.textEditRes.setText(self.table.item(row, 4).text())
            self.textEditData.setText(self.table.item(row, 3).text())

    def terminalText(self, text):
        """pause check"""
        QMessageBox.information(self, '提示', str(text), QMessageBox.Ok)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = LogCheckUI()
    main.show()
    sys.exit(app.exec_())
