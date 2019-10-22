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
startCmd = ''
stopCmd = ''


class WorkThread(QThread):
    """
    子线程，轮询校验结果返回
    """

    add = pyqtSignal(list, list)
    terminal = pyqtSignal(object)

    def run(self):
        global portList, currentPort, startFlag, startCmd

        if not portList or not currentPort:
            return

        try:
            self.serial = TVSerial(port=currentPort, baudrate=115200, timeout=5)
        except Exception as e:
            self.terminal.emit(str(e))
        else:
            cmd_list = r'\n'.strip(startCmd)

            for cmd in cmd_list:
                self.serial.sendComand('\n\n')
                QThread.sleep(self, 2)
                self.serial.sendComand(str(cmd))

            self.serial.s.flushOutput()
            self.serial.s.flushInput()

            startFlag = True

            self.lc = LogCheck()
            while True:
                if not startFlag:
                    self.terminal.emit('正常结束！')
                    break

                try:
                    block = self.serial.s.read(size=1000).decode('utf-8', errors='ignore')
                except Exception as e:
                    pass
                else:
                    if block and block.strip():
                        data, res = self.lc.check_log(block)
                        if data and res:
                            self.add.emit(data, res)
                        print('This is log result from serial!')

                    # 测试代码
                    # data = self.lc.load_log()
                    # res = self.lc.check_log(data)
                    # self.add.emit(data, res)
                    # print('This is log result from local file')


class LogCheckUI(QWidget):
    """
    UI主线程
    """

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """
        initiate app UI
        :return: None
        """
        self.setWindowTitle('日志校验工具')
        self.resize(1000, 700)
        self.setFixedSize(self.width(), self.height())

        font = QFont()
        font.setPointSize(10)
        font.setFamily("Microsoft YaHei UI")

        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(20, 20, 20, 20)
        hboxLayoutHeader = QHBoxLayout()
        hboxLayoutHeader.setContentsMargins(15, 15, 600, 15)
        hboxLayoutHeader.setObjectName('hboxLayoutHeader')
        hboxLayoutBody = QHBoxLayout()
        hboxLayoutBody.setObjectName('hboxLayoutBody')
        # hboxLayoutBody.setContentsMargins(15, 15, 15, 15)
        hboxLayoutFooter = QGridLayout()
        hboxLayoutFooter.setContentsMargins(15, 15, 15, 15)
        hboxLayoutFooter.setObjectName('hboxLayoutFooter')

        self.comboBox = QComboBox()
        self.setFont(font)
        self.comboBox.setCurrentIndex(-1)
        self.refreshBtn = QPushButton('刷新')
        self.refreshBtn.setObjectName('refreshBtn')
        self.refreshBtn.setFont(font)
        self.refreshBtn.setFixedSize(80, 25)

        self.table1 = QTableWidget(0, 5)
        self.table1.setToolTip('点击查看单条日志的详细数据')
        self.table1.setFont(font)
        self.table1.setHorizontalHeaderLabels(['srcEventCode', 'eventCode', 'result', 'detail', 'moreDetail'])
        self.table1.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table1.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table1.setColumnHidden(3, True)
        self.table1.setColumnHidden(4, True)

        self.labelHint1 = QLabel('* 红色 - 日志数据与配置规则不符\n* 绿色 - 日志数据与配置规则相符')
        self.labelHint1.setObjectName('labelHint')
        self.hboxLayoutTable1 = QVBoxLayout()
        self.hboxLayoutTable1.addWidget(self.table1)
        self.hboxLayoutTable1.addWidget(self.labelHint1)

        self.table2 = QTableWidget(0, 2)
        self.table2.setFont(font)
        self.table2.setHorizontalHeaderLabels(['key', 'value'])
        self.table2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table2.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table2.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.labelHint2 = QLabel('* 红色 - value错误\n* 黄色 - key不在配置规则内')
        self.labelHint2.setObjectName('labelHint')
        self.hboxLayoutTable2 = QVBoxLayout()
        self.hboxLayoutTable2.addWidget(self.table2)
        self.hboxLayoutTable2.addWidget(self.labelHint2)

        self.table3 = QTableWidget(0, 1)
        self.table3.setFont(font)
        self.table3.setHorizontalHeaderLabels(['key'])
        self.table3.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table3.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.labelHint3 = QLabel('* 配置规则有定义，但日志数据中缺失\n')
        self.labelHint3.setObjectName('labelHint')
        self.hboxLayoutTable3 = QVBoxLayout()
        self.hboxLayoutTable3.addWidget(self.table3)
        self.hboxLayoutTable3.addWidget(self.labelHint3)

        self.labelCmd1 = QLabel('开始前执行命令')
        self.lineEditCmd1 = QLineEdit()
        self.lineEditCmd1.setObjectName('lineEditCmd1')
        self.labelCmd2 = QLabel('结束后执行命令')
        self.lineEditCmd2 = QLineEdit()
        self.lineEditCmd2.setObjectName('lineEditCmd2')
        try:
            f = open(os.path.join(filePath, 'conf', 'cmd.json'), 'r', encoding='utf-8')
        except FileNotFoundError as e:
            pass
        else:
            cmdDict = json.load(f)
            self.lineEditCmd1.setText(cmdDict['startCmd'])
            self.lineEditCmd2.setText(cmdDict['stopCmd'])
            f.close()

        self.startBtn = QPushButton('开始')
        self.startBtn.setObjectName('startBtn')
        self.startBtn.setFont(font)
        self.startBtn.setFixedSize(80, 25)
        self.stopBtn = QPushButton('停止')
        self.stopBtn.setObjectName('stopBtn')
        self.stopBtn.setFont(font)
        self.stopBtn.setFixedSize(80, 25)
        self.stopBtn.setEnabled(False)

        self.workThread = WorkThread()

        self.comboBox.currentIndexChanged.connect(self.selectionChange)
        self.refreshBtn.clicked.connect(lambda: self.refreshBtnClick(self.refreshBtn))
        self.lineEditCmd1.textChanged.connect(lambda: self.cmdChange(self.lineEditCmd1))
        self.lineEditCmd2.textChanged.connect(lambda: self.cmdChange(self.lineEditCmd2))
        self.table1.cellClicked.connect(self.rowClick)
        self.workThread.add.connect(self.addText)
        self.workThread.terminal.connect(self.terminalText)
        self.startBtn.clicked.connect(self.startBtnClick)
        self.stopBtn.clicked.connect(lambda: self.stopBtnClick(self.stopBtn))

        hboxLayoutHeader.addWidget(self.comboBox)
        hboxLayoutHeader.addWidget(self.refreshBtn)
        hboxLayoutHeader.setStretchFactor(self.comboBox, 2)
        hboxLayoutHeader.setStretchFactor(self.refreshBtn, 1)

        groupBoxTable1 = QGroupBox('校验结果')
        groupBoxTable1.setLayout(self.hboxLayoutTable1)
        groupBoxTable2 = QGroupBox('详细数据')
        groupBoxTable2.setLayout(self.hboxLayoutTable2)
        groupBoxTable3 = QGroupBox('其他数据')
        groupBoxTable3.setLayout(self.hboxLayoutTable3)
        hboxLayoutBody.addWidget(groupBoxTable1)
        hboxLayoutBody.addWidget(groupBoxTable2)
        hboxLayoutBody.addWidget(groupBoxTable3)
        hboxLayoutBody.setStretchFactor(groupBoxTable1, 3)
        hboxLayoutBody.setStretchFactor(groupBoxTable2, 3)
        hboxLayoutBody.setStretchFactor(groupBoxTable3, 1)

        hboxLayoutFooter.addWidget(self.labelCmd1, 0, 0)
        hboxLayoutFooter.addWidget(self.lineEditCmd1, 0, 1)
        hboxLayoutFooter.addWidget(self.startBtn, 0, 2)
        hboxLayoutFooter.addWidget(self.labelCmd2, 1, 0)
        hboxLayoutFooter.addWidget(self.lineEditCmd2, 1, 1)
        hboxLayoutFooter.addWidget(self.stopBtn, 1, 2)

        groupBoxHeader = QGroupBox('请选择正确的端口')
        groupBoxHeader.setObjectName('groupBoxHeader')
        groupBoxHeader.setLayout(hboxLayoutHeader)
        groupBoxFooter = QGroupBox(r'请输入需执行的命令（用\n分隔）')
        groupBoxFooter.setLayout(hboxLayoutFooter)

        mainLayout.addWidget(groupBoxHeader)
        mainLayout.addLayout(hboxLayoutBody)
        mainLayout.addWidget(groupBoxFooter)
        self.setLayout(mainLayout)

    def selectionChange(self, i):
        """
        下拉框选择端口触发
        :param i: object
        :return: None
        """
        global currentPort
        print(self.comboBox.currentText())
        if self.comboBox.currentText():
            currentPort = re.findall(r'COM[0-9]+', self.comboBox.currentText())[0]

    def cmdChange(self, i):
        """
        修改执行命令触发
        :param i: object
        :return: None
        """
        global startCmd, stopCmd

        with open(os.path.join(filePath, 'conf', 'cmd.json'), 'w+', encoding='utf-8') as f:
            if self.lineEditCmd1.text():
                startCmd = self.lineEditCmd1.text()

            if self.lineEditCmd2.text():
                stopCmd = self.lineEditCmd2.text()

            cmdDict = {
                'startCmd': startCmd,
                'stopCmd': stopCmd
            }
            json.dump(cmdDict, f)

    def refreshBtnClick(self, btn):
        """
        点击刷新按钮触发
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
        点击开始按钮触发
        :param btn: object
        :return: None
        """
        global startFlag

        if not currentPort:
            QMessageBox.information(self, '提示', '请选择端口！', QMessageBox.Ok)
            return

        self.row = 0
        self.table1.clearContents()
        self.table2.clearContents()
        self.table3.clearContents()
        self.workThread.start()

        self.comboBox.setEnabled(False)
        self.refreshBtn.setEnabled(False)
        self.lineEditCmd1.setEnabled(False)
        self.lineEditCmd2.setEnabled(False)
        self.startBtn.setEnabled(False)
        self.stopBtn.setEnabled(False)

        # 开始后马上点击结束会报错，添加延时
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(lambda: self.stopBtn.setEnabled(True))
        self.timer.start(5000)
        self.timer.start(5000)

    def stopBtnClick(self, btn):
        """
        点击结束按钮触发
        :param btn: object
        :return: None
        """
        global startFlag, stopCmd

        if not startFlag:
            return

        self.workThread.serial.stopReadSerial()
        if self.labelCmd2.text() and self.labelCmd2.text().strip():
            self.workThread.serial.sendComand(self.labelCmd2.text())
            cmd_list = r'\n'.strip(stopCmd)

            for cmd in cmd_list:
                self.workThread.serial.sendComand('\n\n')
                QThread.sleep(self.workThread, 2)
                self.workThread.serial.sendComand(str(cmd))
        self.workThread.serial.close()

        self.comboBox.setEnabled(True)
        self.refreshBtn.setEnabled(True)
        self.lineEditCmd1.setEnabled(True)
        self.lineEditCmd2.setEnabled(True)
        self.startBtn.setEnabled(True)
        self.stopBtn.setEnabled(False)
        startFlag = False

    def addText(self, data, res):
        """
        获得检验结果返回触发
        :param data: dict
        :param res: dict
        :return: None
        """
        cnt = 0
        for i in res:
            self.table1.setRowCount(self.row + 1)

            self.table1.setItem(self.row, 0,
                                QTableWidgetItem(str(i['src_event_code']) if i['src_event_code'] else 'N/A'))
            self.table1.setItem(self.row, 1, QTableWidgetItem(str(i['event_code']) if i['event_code'] else 'N/A'))
            self.table1.setItem(self.row, 2, QTableWidgetItem('Fail' if i['result'] else 'Pass'))
            self.table1.setItem(self.row, 3, QTableWidgetItem(json.dumps(data[cnt])))
            self.table1.setItem(self.row, 4, QTableWidgetItem(json.dumps(i)))

            cnt += 1
            self.row += 1

    def rowClick(self, row):
        """
        点击基本结果每行数据触发
        :param row: int
        :return: None
        """
        self.table2.clearContents()
        self.table3.clearContents()

        if self.table1.item(row, 3) and self.table1.item(row, 4):
            dictData = json.loads(self.table1.item(row, 3).text())
            dictRes = json.loads(self.table1.item(row, 4).text())

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
        子线程结束触发提示
        :param text: str
        :return:
        """
        global startFlag

        self.comboBox.setEnabled(True)
        self.refreshBtn.setEnabled(True)
        self.lineEditCmd1.setEnabled(True)
        self.lineEditCmd2.setEnabled(True)
        self.startBtn.setEnabled(True)
        self.stopBtn.setEnabled(False)
        startFlag = False
        QMessageBox.information(self, '提示', text, QMessageBox.Ok)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = LogCheckUI()
    qssstyle = '''
        .QComboBox {
            border:1px solid #8f8f91;
            border-radius:4px;
        }
        .QTableWidget {
            border:1px solid #8f8f91;
            margin-left:5px;
            margin-right:5px;
        }
        .QLabel#labelHint {
            margin-left:5px;
            margin-right:5px;
        }
        .QPushButton#refreshBtn {
            border:1px solid #8f8f91;
            border-radius:4px;
            position:relative;
            margin-left:5px;
            max-width:80px;
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
        .QLineEdit#lineEditCmd1 {
            border:1px solid #8f8f91;
            border-radius:4px;
            margin-left:5px;
            margin-right:5px;
            width:200px;
        }
        .QLineEdit#lineEditCmd2 {
            border:1px solid #8f8f91;
            border-radius:4px;
            margin-left:5px;
            margin-right:5px;
            width:200px;
        }
    '''
    main.setStyleSheet(qssstyle)
    main.show()
    sys.exit(app.exec_())
