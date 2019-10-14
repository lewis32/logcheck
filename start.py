# pylint: disable-msg=invalid-name,global-statement

import os
import json
import sys
import re
import qdarkstyle
from core.log_check import *
from core.package.myserial import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

filePath = os.path.abspath((os.path.dirname(os.path.realpath(__file__))))
isStarted = False
portList = []
currentPort = None
cmd = '\n\nlog.off\ntail -f /var/local/logservice/logfile/tmp*\n'


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
            # self.serial.sendComand('\n\nlog.off\n')
            # self.sleep(1)
            # self.serial.sendComand('tail -f /var/local/logservice/logfile/tmp*\n')
            with open(os.path.join(filePath, 'conf', 'cmd.txt'), 'r', encoding='utf-8') as f:
                self.serial.sendComand(str(f.readline()))

            self.serial.startReadSerial()
            isStarted = True
            self.serial.s.flushInput()
            self.serial.s.flushOutput()
            
            self.lc = LogCheck()
            while True:
                if not isStarted:
                    self.terminal.emit('正常结束！')
                    break

                try:
                    block = self.serial.s.readline().decode('utf-8', errors='ignore')

                except Exception as e:
                    pass

                else:
                    if block and block.strip():
                        res = self.lc.check_log(block)
                        self.add.emit(block, res)
                        print('test11111111111111111')

                    # 测试代码
                    data = self.lc.load_log()
                    res = self.lc.check_log(data)
                    self.add.emit(data, res)
                    print('test000000000000')


class LogCheckUI(QWidget):
    """
    UI main thread
    """

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """
        initiate app UI
        :return: None
        """
        self.setWindowTitle('LogCheck')
        self.resize(900, 450)

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(20, 20, 20, 20)
        hboxLayoutHead = QHBoxLayout()
        hboxLayoutHead.setContentsMargins(0, 0, 590, 0)
        hboxLayoutHead.setObjectName('hboxLayoutHead')
        hboxLayoutFooter = QHBoxLayout()
        hboxLayoutFooter.setObjectName('hboxLayoutFooter')
        # hboxLayoutFooter.setContentsMargins(400, 0, 0, 0)
        hboxLayoutBody = QHBoxLayout()
        hboxLayoutBody.setObjectName('hboxLayoutBody')

        font = QFont()
        font.setPointSize(10)
        font.setFamily("Microsoft YaHei UI")
        self.comboBox = QComboBox()
        self.setFont(font)
        self.comboBox.setCurrentIndex(-1)
        self.flushBtn = QPushButton('刷新')
        self.flushBtn.setObjectName('flushBtn')
        self.flushBtn.setFont(font)

        self.table = QTableWidget(1, 5)
        self.table.setToolTip('点击查看原始数据和详细结果')
        self.table.setFont(font)
        self.table.setHorizontalHeaderLabels(['上级事件码', '本级事件码', '验证结果', '日志数据', '结果详情'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setColumnHidden(3, True)
        self.table.setColumnHidden(4, True)
        # self.row = 0

        # self.textEditData = QTextEdit()
        # self.textEditData.setReadOnly(True)
        # self.textEditData.setToolTip('原始数据')
        self.textEditData = QTableWidget(0, 2)
        self.textEditData.setReadOnly(True)
        self.textEditData.setHorizontalHeaderLabels(['key', 'value'])
        self.textEditData.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.textEditData.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.textEditRes = QTextEdit()
        self.textEditRes.setReadOnly(True)
        self.textEditRes.setToolTip('详细结果')
        self.textEditInput = QLineEdit()
        self.textEditInput.setObjectName('textEditInput')
        # self.textEditInput.resize(800, 2000)
        self.startBtn = QPushButton('开始')
        self.startBtn.setObjectName('startBtn')
        self.startBtn.setFont(font)
        self.stopBtn = QPushButton('停止')
        self.stopBtn.setObjectName('stopBtn')
        self.stopBtn.setEnabled(False)
        self.stopBtn.setFont(font)
        self.workThread = WorkThread()

        self.comboBox.currentIndexChanged.connect(self.selectionChange)
        self.flushBtn.clicked.connect(lambda: self.flushBtnClick(self.flushBtn))
        self.textEditInput.textChanged.connect(lambda: self.cmdChange(self.textEditInput))
        self.table.cellClicked.connect(self.itemClick)
        self.workThread.add.connect(self.addText)
        self.workThread.terminal.connect(self.terminalText)
        self.startBtn.clicked.connect(self.startBtnClick)
        self.stopBtn.clicked.connect(lambda: self.stopBtnClick(self.stopBtn))

        hboxLayoutHead.addWidget(self.comboBox)
        hboxLayoutHead.addWidget(self.flushBtn)
        hboxLayoutHead.setStretchFactor(self.comboBox, 2)
        hboxLayoutHead.setStretchFactor(self.flushBtn, 1)
        mainLayout.addLayout(hboxLayoutHead)
        hboxLayoutBody.addWidget(self.table)
        hboxLayoutBody.addWidget(self.textEditData)
        hboxLayoutBody.addWidget(self.textEditRes)
        hboxLayoutBody.setStretchFactor(self.table, 1)
        hboxLayoutBody.setStretchFactor(self.textEditData, 1)
        hboxLayoutBody.setStretchFactor(self.textEditRes, 1)
        mainLayout.addLayout(hboxLayoutBody)
        hboxLayoutFooter.addWidget(self.textEditInput)
        hboxLayoutFooter.addWidget(self.startBtn)
        hboxLayoutFooter.addWidget(self.stopBtn)
        hboxLayoutFooter.setStretchFactor(self.textEditInput, 8)
        hboxLayoutFooter.setStretchFactor(self.startBtn, 1)
        hboxLayoutFooter.setStretchFactor(self.stopBtn, 1)
        mainLayout.addLayout(hboxLayoutFooter)
        mainLayout.setStretchFactor(hboxLayoutHead, 1)
        mainLayout.setStretchFactor(hboxLayoutBody, 4)
        mainLayout.setStretchFactor(hboxLayoutFooter, 1)

        self.setLayout(mainLayout)

    def selectionChange(self, i):
        """
        select port and save its value
        :param i: object
        :return: None
        """
        global currentPort
        print(self.comboBox.currentText())
        if self.comboBox.currentText():
            currentPort = re.findall(r'COM[0-9]+', self.comboBox.currentText())[0]

    def cmdChange(self, i):
        """
        receive text in textEdit area
        :param i: object
        :return: None
        """
        global cmd
        if self.textEditInput.text():
            cmd = self.textEditInput.text()

            with open(os.path.join(filePath, 'conf', 'cmd.txt'), 'w+', encoding='utf-8') as f:
                f.write(cmd)

    def flushBtnClick(self, btn):
        """
        click refresh button
        :param btn: object
        :return: None
        """
        global portList, currentPort

        self.comboBox.clear()
        portList = getPortList()
        if portList:
            for i in portList:
                self.comboBox.addItem(str(i))
        self.comboBox.setCurrentIndex(-1)
        currentPort = None


    def startBtnClick(self, btn):
        """
        click start button
        :param btn: object
        :return: None
        """
        print(currentPort)
        if not currentPort:
            QMessageBox.information(self, '提示', '请选择端口！', QMessageBox.Ok)
            return

        self.table.clearContents()
        self.row = 0
        self.table.setRowCount(self.row + 1)
        self.comboBox.setEnabled(False)
        self.flushBtn.setEnabled(False)
        self.startBtn.setEnabled(False)
        self.stopBtn.setEnabled(False)
        self.workThread.start()

        # 开始后马上点击结束会报错，添加延时
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(lambda: self.stopBtn.setEnabled(True))
        self.timer.start(5000)

    def stopBtnClick(self, btn):
        """
        click terminal button
        :param btn: object
        :return: None
        """
        global isStarted

        self.workThread.serial.stopReadSerial()
        self.workThread.serial.close()

        self.comboBox.setEnabled(True)
        self.flushBtn.setEnabled(True)
        self.startBtn.setEnabled(True)
        self.stopBtn.setEnabled(False)
        isStarted = False

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
        click item and display detail info
        """
        if self.table.item(row, 3) and self.table.item(row, 4):
            self.textEditRes.setText(self.table.item(row, 4).text())
            self.textEditData.setText(self.table.item(row, 3).text())
            dictData = json.loads(self.table.item(row, 3).text())
            for k, v in dictData:
                self.textEditData.

    def terminalText(self, text):
        """
        pause check
        """
        QMessageBox.information(self, '提示', str(text), QMessageBox.Ok)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = LogCheckUI()
    qssstyle = '''
        .QComboBox {
            border:1px solid #8f8f91;
            border-radius:4px;
        }
        .QPushButton#flushBtn {
            border:1px solid #8f8f91;
            border-radius:4px;
            position:relative;
            margin-left:5px;
        }
        .QPushButton#startBtn {
            border:1px solid #8f8f91;
            border-radius:4px;
            position:relative;
            margin-right:10px;
            margin-left:5px;
        }
        .QPushButton#startBtn {
            border:1px solid #8f8f91;
            border-radius:4px;
            margin-right:5px;
            margin-left:5px;
        }
        .QPushButton#stopBtn {
            border:1px solid #8f8f91;
            border-radius:4px;
            margin-right:5px;
            margin-left:5px;
        }
    '''
    main.setStyleSheet(qssstyle)
    # main.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    main.show()
    sys.exit(app.exec_())
