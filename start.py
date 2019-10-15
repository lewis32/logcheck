# pylint: disable-msg=invalid-name,global-statement

from core.log_check import *
from core.package.myserial import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

filePath = os.path.abspath((os.path.dirname(os.path.realpath(__file__))))
startFlag = False
portList = []
currentPort = None
cmd = '\n\nlog.off\n\ntail -f /var/local/logservice/logfile/tmp*\n'

class WorkThread(QThread):
    """
    循环读取校验结果的子进程
    """

    add = pyqtSignal(list, list)
    terminal = pyqtSignal(object)

    def run(self):
        global portList, currentPort, startFlag

        if not portList or not currentPort:
            return

        try:
            self.serial = TVSerial(port=currentPort, baudrate=115200, timeout=5)

        except Exception as e:
            self.terminal.emit(e)

        else:
            with open(os.path.join(filePath, 'conf', 'cmd.txt'), 'r', encoding='utf-8') as f:
                self.serial.sendComand(str(f.readline()))

            self.serial.startReadSerial()
            self.serial.s.flushInput()
            self.serial.s.flushOutput()
            startFlag = True
            
            self.lc = LogCheck()
            while True:
                if not startFlag:
                    self.terminal.emit('正常结束！')
                    break

                try:
                    block = self.serial.s.readline().decode('utf-8', errors='ignore')

                except Exception as e:
                    print(e)

                else:
                    if block and block.strip():
                        res = self.lc.check_log(block)
                        self.add.emit(block, res)
                        print('This is log result from serial!')

                    # 测试代码
                    data = self.lc.load_log()
                    res = self.lc.check_log(data)
                    self.add.emit(data, res)
                    print('This is log result from local file')


class LogCheckUI(QWidget):
    """
    UI主进程
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
        hboxLayoutBody = QHBoxLayout()
        hboxLayoutBody.setObjectName('hboxLayoutBody')
        hboxLayoutFooter = QGridLayout()
        hboxLayoutFooter.setObjectName('hboxLayoutFooter')
        # hboxLayoutFooter.setContentsMargins(400, 0, 0, 0)

        font = QFont()
        font.setPointSize(10)
        font.setFamily("Microsoft YaHei UI")
        self.comboBox = QComboBox()
        self.setFont(font)
        self.comboBox.setCurrentIndex(-1)
        self.flushBtn = QPushButton('刷新')
        self.flushBtn.setObjectName('flushBtn')
        self.flushBtn.setFont(font)

        self.table1 = QTableWidget(0, 5)
        self.table1.setToolTip('点击查看原始数据和详细结果')
        self.table1.setFont(font)
        self.table1.setHorizontalHeaderLabels(['上级事件码', '本级事件码', '验证结果', '日志数据', '结果详情'])
        self.table1.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table1.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table1.setColumnHidden(3, True)
        self.table1.setColumnHidden(4, True)
        # self.row = 0

        self.table2 = QTableWidget(0, 2)
        self.table2.setToolTip('基本结果')
        self.table2.setFont(font)
        self.table2.setHorizontalHeaderLabels(['Key', 'Value'])
        self.table2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table2.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table2.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.table3 = QTableWidget(0, 1)
        self.table3.setToolTip('其他结果')
        self.table3.setFont(font)
        self.table3.setHorizontalHeaderLabels(['缺少键值'])
        self.table3.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table3.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.labelCmd = QLabel('开始前执行命令')
        self.lineEditCmd = QLineEdit()
        self.lineEditCmd.setObjectName('textEditInput')
        with open(os.path.join(filePath, 'conf', 'cmd.txt'), 'r', encoding='utf-8') as f:
            self.lineEditCmd.setText(f.readline())

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
        self.lineEditCmd.textChanged.connect(lambda: self.cmdChange(self.lineEditCmd))
        self.table1.cellClicked.connect(self.rowClick)
        self.workThread.add.connect(self.addText)
        self.workThread.terminal.connect(self.terminalText)
        self.startBtn.clicked.connect(self.startBtnClick)
        self.stopBtn.clicked.connect(lambda: self.stopBtnClick(self.stopBtn))

        hboxLayoutHead.addWidget(self.comboBox)
        hboxLayoutHead.addWidget(self.flushBtn)
        hboxLayoutHead.setStretchFactor(self.comboBox, 2)
        hboxLayoutHead.setStretchFactor(self.flushBtn, 1)
        mainLayout.addLayout(hboxLayoutHead)
        hboxLayoutBody.addWidget(self.table1)
        hboxLayoutBody.addWidget(self.table2)
        hboxLayoutBody.addWidget(self.table3)
        hboxLayoutBody.setStretchFactor(self.table1, 2)
        hboxLayoutBody.setStretchFactor(self.table2, 3)
        hboxLayoutBody.setStretchFactor(self.table3, 1)
        mainLayout.addLayout(hboxLayoutBody)
        self.view.add
        hboxLayoutFooter.addWidget(self.view)
        hboxLayoutFooter.addWidget(self.labelCmd)
        hboxLayoutFooter.addWidget(self.lineEditCmd)
        hboxLayoutFooter.addWidget(self.startBtn)
        hboxLayoutFooter.addWidget(self.stopBtn)
        hboxLayoutFooter.setStretchFactor(self.labelCmd, 1)
        hboxLayoutFooter.setStretchFactor(self.lineEditCmd, 8)
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
        if self.lineEditCmd.text():
            cmd = self.lineEditCmd.text()

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

        self.table1.clearContents()
        self.row = 0
        self.table1.setRowCount(self.row + 1)
        self.comboBox.setEnabled(False)
        self.flushBtn.setEnabled(False)
        self.lineEditCmd.setEnabled(False)
        self.startBtn.setEnabled(False)
        self.stopBtn.setEnabled(False)
        self.workThread.start()

        # 开始后马上点击结束会报错，添加延时
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(lambda: self.stopBtn.setEnabled(True))
        self.timer.start(5000)
        self.timer.start(5000)

    def stopBtnClick(self, btn):
        """
        click terminal button
        :param btn: object
        :return: None
        """
        global startFlag

        self.workThread.serial.stopReadSerial()
        self.workThread.serial.close()

        self.comboBox.setEnabled(True)
        self.flushBtn.setEnabled(True)
        self.lineEditCmd.setEnabled(True)
        self.startBtn.setEnabled(True)
        self.stopBtn.setEnabled(False)
        startFlag = False

    def addText(self, data, res):
        """
        add check result
        :param data: dict
        :param res: dict
        :return: None
        """
        print('test addText')
        cnt = 0
        for i in res:
            self.table1.setRowCount(self.row + 1)

            self.table1.setItem(self.row, 0, QTableWidgetItem(str(i['src_event_code']) if i['src_event_code'] else 'N/A'))
            self.table1.setItem(self.row, 1, QTableWidgetItem(str(i['event_code']) if i['event_code'] else 'N/A'))
            self.table1.setItem(self.row, 2, QTableWidgetItem('不通过' if i['result'] else '通过'))
            self.table1.setItem(self.row, 3, QTableWidgetItem(json.dumps(data[cnt])))
            self.table1.setItem(self.row, 4, QTableWidgetItem(json.dumps(i)))

            cnt += 1
            self.row += 1
            print('addText: row is %s' % self.row)

    def rowClick(self, row):
        """
        click item and display detail info
        :param row: int
        :return: None
        """
        self.table2.clearContents()
        self.table3.clearContents()

        if self.table1.item(row, 3) and self.table1.item(row, 4):
            dictData = json.loads(self.table1.item(row, 3).text())
            dictRes = json.loads(self.table1.item(row, 4).text())
            print(dictRes)

            n = 0
            for k in dictData:
                self.table2.setRowCount(n + 1)
                self.table2.setItem(n, 0, QTableWidgetItem(str(k)))
                self.table2.setItem(n, 1, QTableWidgetItem(str(dictData[k])))

                if k in dictRes['invalid_key']:
                    self.table2.item(n, 0).setBackground(QBrush(QColor(255, 0, 0)))
                    self.table2.item(n, 1).setBackground(QBrush(QColor(255, 0, 0)))
                if k in dictRes['undefined_key']:
                    self.table2.item(n, 0).setBackground(QBrush(QColor(255, 255, 0)))
                    self.table2.item(n, 1).setBackground(QBrush(QColor(255, 255, 0)))
                n += 1

            m = 0
            for i in dictRes['missing_key']:
                self.table3.setRowCount(m + 1)
                self.table3.setItem(m, 0, QTableWidgetItem(str(i)))
                m += 1

    def terminalText(self, text):
        """
        pause check
        :param text: str
        :return:
        """
        QMessageBox.information(self, '提示', text, QMessageBox.Ok)


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
    main.show()
    sys.exit(app.exec_())
