#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable-msg=invalid-name,global-statement,typo

import sys
from core.log_check import *
from core.package.myserial import *
from core.package.mylogging import MyLogging as Logging
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

filePath = os.path.abspath((os.path.dirname(os.path.realpath(__file__))))
startFlag = False
portList = []
currentPort = None
cmdStart = ''
cmdStop = ''


class WorkThread(QThread):
    """
    子线程，轮询校验结果返回
    """
    add = pyqtSignal(list)
    terminal = pyqtSignal(object)
    logger = Logging(__name__)

    def run(self):
        global currentPort, startFlag, cmdStart

        if not currentPort:
            return

        try:
            self.serial = TVSerial(port=currentPort, baudrate=115200, timeout=5)
        except Exception as e:
            self.terminal.emit(str(e))
        else:
            self.logger.info("Start command: " + cmdStart)

            self.serial.sendComand('\n\n')
            self.sleep(1)
            self.serial.sendComand(cmdStart)
            self.serial.sendComand('\n\n')
            self.sleep(1)

            self.serial.s.flushOutput()
            self.serial.s.flushInput()

            startFlag = True

            self.lc = LogCheck()
            while True:
                if not startFlag:
                    self.terminal.emit('正常结束！')
                    break

                try:
                    block = self.serial.s.read(size=10000).decode(
                        'utf-8', errors='ignore')
                except Exception as e:
                    self.logger.error("Error occurs while reading serial: "
                                      + str(e))
                else:
                    if block and block.strip():
                        self.logger.info('Original log data: ' + block)
                        res = self.lc.check_log(block)
                        if res:
                            self.add.emit(res)
                        self.logger.info('Check result: ' + str(res))

                    # 测试代码
                    # data = self.lc.load_log()
                    # res = self.lc.check_log(data)
                    # self.add.emit(data, res)
                    # print('This is log result from local file')


class LogCheckUI(QTabWidget):
    """
    UI主线程
    """

    def __init__(self):
        """
        初始化整体UI
        :return: None
        """
        super().__init__()
        self.logger = Logging(__name__)

        self.setWindowTitle('日志检验工具')
        self.resize(1000, 700)
        self.setFixedSize(self.width(), self.height())

        self.font = QFont()
        self.font.setPointSize(10)
        self.font.setFamily("Microsoft YaHei UI")

        self.tabAutoMode = QWidget()
        self.tabManualMode = QWidget()
        self.addTab(self.tabAutoMode, '自动模式')
        self.addTab(self.tabManualMode, '手动模式')
        self.initAutoModeUI()
        self.initManualModeUI()

    def initAutoModeUI(self):
        """
        初始化自动模式UI
        :return: None
        """
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(20, 20, 20, 20)
        self.hboxLayoutHeader = QHBoxLayout()
        self.hboxLayoutHeader.setContentsMargins(15, 15, 600, 15)
        self.hboxLayoutHeader.setObjectName('hboxLayoutHeader')
        self.hboxLayoutBody = QHBoxLayout()
        self.hboxLayoutBody.setObjectName('hboxLayoutBody')
        # hboxLayoutBody.setContentsMargins(15, 15, 15, 15)
        self.hboxLayoutFooter = QGridLayout()
        self.hboxLayoutFooter.setContentsMargins(15, 15, 15, 15)
        self.hboxLayoutFooter.setObjectName('hboxLayoutFooter')

        self.comboBox = QComboBox()
        self.setFont(self.font)
        self.comboBox.setCurrentIndex(-1)
        self.btnRefresh = QPushButton('刷新')
        self.btnRefresh.setObjectName('btnRefresh')
        self.btnRefresh.setFont(self.font)
        self.btnRefresh.setFixedSize(80, 25)
        self.btnClear = QPushButton('清空数据')
        self.btnClear.setObjectName('btnClearCells')
        self.btnClear.setFont(self.font)
        self.btnClear.setFixedSize(100, 25)

        self.tableLeft = QTableWidget(0, 5)
        self.tableLeft.setToolTip('点击查看详细结果，右键复制原始数据')
        self.tableLeft.setMouseTracking(True)
        self.tableLeft.setFont(self.font)
        self.tableLeft.setHorizontalHeaderLabels(
            ['SrcEventCode', 'EventCode', 'Result', 'Detail', 'MoreDetail'])
        self.tableLeft.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.tableLeft.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents)
        self.tableLeft.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableLeft.setColumnHidden(3, True)
        self.tableLeft.setColumnHidden(4, True)

        self.hboxLayoutTableLeft = QVBoxLayout()
        self.hboxLayoutTableLeft.addWidget(self.tableLeft)

        self.tableMid = QTableWidget(0, 2)
        # self.tableMid.setSortingEnabled(True)
        # self.tableMid.sortByColumn(0, Qt.AscendingOrder)
        self.tableMid.setFont(self.font)
        self.tableMid.setHorizontalHeaderLabels(['Key', 'Value'])
        self.tableMid.verticalHeader().setVisible(False)
        self.tableMid.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.tableMid.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents)
        self.tableMid.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.hboxLayoutTableMid = QVBoxLayout()
        self.hboxLayoutTableMid.addWidget(self.tableMid)

        self.tableRight = QTableWidget(0, 2)
        # self.tableRight.setSortingEnabled(True)
        self.tableRight.setFont(self.font)
        self.tableRight.setHorizontalHeaderLabels(['Key', 'Value'])
        self.tableRight.verticalHeader().setVisible(False)
        self.tableRight.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.tableRight.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents)
        self.tableRight.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.hboxLayoutTableRight = QVBoxLayout()
        self.hboxLayoutTableRight.addWidget(self.tableRight)

        self.labelCmdBeforeStart = QLabel('开始前执行命令')
        self.lineEditCmdBeforeStart = QLineEdit()
        self.lineEditCmdBeforeStart.setObjectName('lineEditCmdBeforeStart')
        self.labelCmdAfterStop = QLabel('结束后执行命令')
        self.lineEditCmdAfterStop = QLineEdit()
        self.lineEditCmdAfterStop.setReadOnly(True)
        self.lineEditCmdAfterStop.setObjectName('lineEditCmdAfterStop')
        try:
            f = open(os.path.join(
                filePath, 'conf', 'setting.json'), mode='r', encoding='utf-8')
        except FileNotFoundError as e:
            self.logger.error("File not found: " + str(e))
        else:
            cmdDict = json.load(f)
            self.lineEditCmdBeforeStart.setText(cmdDict['startCmd'])
            self.lineEditCmdAfterStop.setText(cmdDict['stopCmd'])
            f.close()

            global cmdStart, cmdStop
            cmdStart = cmdDict['startCmd']
            cmdStop = cmdDict['stopCmd']

        self.btnStart = QPushButton('开始')
        self.btnStart.setObjectName('btnStart')
        self.btnStart.setFont(self.font)
        self.btnStart.setFixedSize(80, 25)
        self.btnStop = QPushButton('停止')
        self.btnStop.setObjectName('btnStop')
        self.btnStop.setFont(self.font)
        self.btnStop.setFixedSize(80, 25)
        self.btnStop.setEnabled(False)

        self.workThread = WorkThread()

        self.comboBox.currentIndexChanged.connect(self.comboBoxSelected)
        self.btnRefresh.clicked.connect(
            lambda: self.btnRefreshClicked(self.btnRefresh))
        self.btnClear.clicked.connect(
            lambda: self.btnClearClicked(self.btnClear))
        self.btnStart.clicked.connect(self.btnStartClicked)
        self.btnStop.clicked.connect(
            lambda: self.btnStopClicked(self.btnStop))
        self.lineEditCmdBeforeStart.textChanged.connect(
            lambda: self.lineEditCmdChanged(self.lineEditCmdBeforeStart))
        self.lineEditCmdAfterStop.textChanged.connect(
            lambda: self.lineEditCmdChanged(self.lineEditCmdAfterStop))
        self.tableLeft.cellClicked.connect(self.tableLeftCellClicked)
        self.tableMid.cellClicked.connect(self.tableMidCellClicked)
        # self.tableLeft.popCellTip.connect(
        # lambda: self.popCellTip(self.tableLeft))
        self.workThread.add.connect(self.checkResultReceived)
        self.workThread.terminal.connect(self.stopSignalReceived)

        self.hboxLayoutHeader.addWidget(self.comboBox)
        self.hboxLayoutHeader.addWidget(self.btnRefresh)
        self.hboxLayoutHeader.addWidget(self.btnClear)
        self.hboxLayoutHeader.setStretchFactor(self.comboBox, 2)
        self.hboxLayoutHeader.setStretchFactor(self.btnRefresh, 1)

        self.groupBoxTable1 = QGroupBox('校验结果')
        self.groupBoxTable1.setLayout(self.hboxLayoutTableLeft)
        self.groupBoxTable2 = QGroupBox('一级数据')
        self.groupBoxTable2.setLayout(self.hboxLayoutTableMid)
        self.groupBoxTable3 = QGroupBox('二级数据')
        self.groupBoxTable3.setLayout(self.hboxLayoutTableRight)
        self.hboxLayoutBody.addWidget(self.groupBoxTable1)
        self.hboxLayoutBody.addWidget(self.groupBoxTable2)
        self.hboxLayoutBody.addWidget(self.groupBoxTable3)
        self.hboxLayoutBody.setStretchFactor(self.groupBoxTable1, 7)
        self.hboxLayoutBody.setStretchFactor(self.groupBoxTable2, 7)
        self.hboxLayoutBody.setStretchFactor(self.groupBoxTable3, 5)

        self.hboxLayoutFooter.addWidget(self.labelCmdBeforeStart, 0, 0)
        self.hboxLayoutFooter.addWidget(self.lineEditCmdBeforeStart, 0, 1)
        self.hboxLayoutFooter.addWidget(self.btnStart, 0, 2)
        self.hboxLayoutFooter.addWidget(self.labelCmdAfterStop, 1, 0)
        self.hboxLayoutFooter.addWidget(self.lineEditCmdAfterStop, 1, 1)
        self.hboxLayoutFooter.addWidget(self.btnStop, 1, 2)

        self.groupBoxHeader = QGroupBox('选择端口')
        self.groupBoxHeader.setObjectName('groupBoxHeader')
        self.groupBoxHeader.setLayout(self.hboxLayoutHeader)
        self.groupBoxFooter = QGroupBox(r'输入命令')
        self.groupBoxFooter.setLayout(self.hboxLayoutFooter)

        self.mainLayout.addWidget(self.groupBoxHeader)
        self.mainLayout.addLayout(self.hboxLayoutBody)
        self.mainLayout.addWidget(self.groupBoxFooter)
        self.tabAutoMode.setLayout(self.mainLayout)

    def initManualModeUI(self):
        """
        初始化手动模式UI
        :return: None
        """

    def comboBoxSelected(self, i):
        """
        下拉框选择端口触发
        :param i: object
        :return: None
        """
        global currentPort
        self.logger.info("Text in combobox: " + self.comboBox.currentText())

        if self.comboBox.currentText():
            currentPort = re.findall(
                r'COM[0-9]+', self.comboBox.currentText())[0]

    def lineEditCmdChanged(self, i):
        """
        修改执行命令触发
        :param i: object
        :return: None
        """
        global cmdStart, cmdStop

        with open(os.path.join(
                filePath, 'conf', 'setting.json'), 'w+', encoding='utf-8') as f:
            if self.lineEditCmdBeforeStart.text():
                cmdStart = self.lineEditCmdBeforeStart.text()

            if self.lineEditCmdAfterStop.text():
                cmdStop = self.lineEditCmdAfterStop.text()

            cmdDict = {
                'startCmd': cmdStart,
                'stopCmd': cmdStop
            }
            json.dump(cmdDict, f, indent=4)

    def btnRefreshClicked(self, btn):
        """
        点击刷新按钮触发
        :param btn: object
        :return: None
        """
        self.comboBox.clear()
        try:
            portList = getPortList()
        except Exception as e:
            self.logger.error("Error occurs while get port list: " + str(e))
            QMessageBox.information(self, '提示', str(e), QMessageBox.Ok)
        else:
            if portList:
                for i in portList:
                    try:
                        # self.comboBox.addItem(re.match(r'^(COM\d).*', str(i)).group(1))
                        self.comboBox.addItem(i[0])
                    except Exception as e:
                        self.logger.error(str(e))


    def btnClearClicked(self, btn):
        """
        点击清空按钮触发
        :param btn: object
        :return: None
        """
        self.tableLeft.clearContents()
        self.tableMid.clearContents()
        self.tableRight.clearContents()
        self.row = 0

    def btnStartClicked(self, btn):
        """
        点击开始按钮触发
        :param btn: object
        :return: None
        """
        global startFlag

        if not currentPort:
            QMessageBox.information(self, '提示', '请先选择端口！',
                QMessageBox.Ok)
            return

        self.row = 0
        self.tableLeft.clearContents()
        self.tableMid.clearContents()
        self.tableRight.clearContents()
        self.workThread.start()

        self.comboBox.setEnabled(False)
        self.btnRefresh.setEnabled(False)
        self.lineEditCmdBeforeStart.setEnabled(False)
        self.lineEditCmdAfterStop.setEnabled(False)
        self.btnStart.setEnabled(False)
        self.btnStop.setEnabled(False)

        # 开始后马上点击结束会报错，添加延时
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(lambda: self.btnStop.setEnabled(True))
        self.timer.start(5000)
        self.timer.start(5000)

    def btnStopClicked(self, btn):
        """
        点击结束按钮触发
        :param btn: object
        :return: None
        """
        global startFlag, cmdStop

        if not startFlag:
            QMessageBox.information(
                self, '提示', '串口异常，重启后尝试！', QMessageBox.Ok)
            return
        self.workThread.serial.stopReadSerial()
        # TODO
        # if self.lineEditCmdAfterStop.text()
        # and self.lineEditCmdAfterStop.text().strip():
        #     self.workThread.serial.sendComand(
        # self.lineEditCmdAfterStop.text())
        #     cmd_list = re.split(r'\\n', stopCmd)
        #     self.logger.info("Command List: " + str(cmd_list))
        #
        #     for cmd in cmd_list:
        #         self.workThread.serial.sendComand('\n\n')
        #         self.workThread.sleep(1)
        #         self.workThread.serial.sendComand(str(cmd))
        #         self.logger.info("Execute command: " + str(cmd))
        self.workThread.serial.close()

        self.comboBox.setEnabled(True)
        self.btnRefresh.setEnabled(True)
        self.lineEditCmdBeforeStart.setEnabled(True)
        self.lineEditCmdAfterStop.setEnabled(True)
        self.btnStart.setEnabled(True)
        self.btnStop.setEnabled(False)
        startFlag = False

    def checkResultReceived(self, res):
        """
        获得检验结果返回触发
        :param data: dict
        :param res: dict
        :return: None
        """
        cnt = 0

        if not res:
            return

        for i in res:
            self.tableLeft.setRowCount(self.row + 1)
            self.tableLeft.setItem(self.row, 0, QTableWidgetItem(
                str(i['src_event_code']) if i['src_event_code'] else 'N/A'))
            self.tableLeft.setItem(self.row, 1, QTableWidgetItem(
                str(i['event_code']) if i['event_code'] else 'N/A'))

            if i['result'] == -1:
                self.tableLeft.setItem(self.row, 2, QTableWidgetItem('N/A'))
                # 灰色表示从配置文件中找不到对应的事件
                self.tableLeft.item(self.row, 2).setBackground(
                    QBrush(QColor(211, 211, 211)))
                self.setToolTip('配置文件中没有对应的eventcode！')
            if i['result'] == 0:
                self.tableLeft.setItem(self.row, 2, QTableWidgetItem('Pass'))
                # 绿色表示全部字段均正常
                self.tableLeft.item(self.row, 2).setBackground(
                    QBrush(QColor(0, 128, 0)))
                # fontLight = QFont()
                # fontLight.setStyle()
                # self.tableLeft.item(self.row, 2).setFont(QFont(QFont="White"))
                self.setToolTip('所有字段均正常，Ctrl+C可复制内容')
            if i['result'] == 1:
                self.tableLeft.setItem(self.row, 2, QTableWidgetItem('Fail'))
                # 红色表示部分字段缺失或值错误
                self.tableLeft.item(self.row, 2).setBackground(
                    QBrush(QColor(255, 0, 0)))
                self.setToolTip('部分字段缺失或错误，Ctrl+C可复制内容')
            if i['result'] == 2:
                self.tableLeft.setItem(self.row, 2,
                                       QTableWidgetItem('Warning'))
                # 黄色表示包含未定义字段
                elf.tableLeft.item(self.row, 2).setBackground(
                    QBrush(QColor(255, 255, 0)))
                self.setToolTip('部分字段不在定义内，Ctrl+C可复制内容')

            # self.table1.setItem(self.row, 2, QTableWidgetItem(
            #     'Fail' if i['result'] else 'Pass'))
            self.tableLeft.setItem(self.row, 3, QTableWidgetItem(
                json.dumps(i['data'])))
            self.tableLeft.setItem(self.row, 4, QTableWidgetItem(
                json.dumps(i)))

            # textEdit.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            # textEdit.customContextMenuRequested[QtCore.QPoint].connect(
            #     self.myListWidgetContext)

            cnt += 1
            self.row += 1

    def tableLeftCellClicked(self, row):
        """
        点击基本结果每行数据触发
        :param row: int
        :return: None
        """
        try:
            self.tableMid.clearContents()
            self.tableRight.clearContents()

            if self.tableLeft.item(row, 3) and self.tableLeft.item(row, 4):
                self.tableMid.setSortingEnabled(False)
                dictData = json.loads(self.tableLeft.item(row, 3).text())
                dictRes = json.loads(self.tableLeft.item(row, 4).text())
                n = 0
                for k in dictData:
                    self.tableMid.setRowCount(n + 1)
                    self.tableMid.setItem(n, 0, QTableWidgetItem(str(k)))
                    self.tableMid.setItem(n, 1, QTableWidgetItem(str(dictData[k])))

                    if k in dictRes['invalid_key']:
                        self.tableMid.item(n, 0).setBackground(
                            QBrush(QColor(255, 0, 0)))
                        self.tableMid.item(n, 1).setBackground(
                            QBrush(QColor(255, 0, 0)))

                    if k in dictRes['undefined_key']:
                        self.tableMid.item(n, 0).setBackground(
                            QBrush(QColor(255, 255, 0)))
                        self.tableMid.item(n, 1).setBackground(
                            QBrush(QColor(255, 255, 0)))
                    n += 1

                for i in dictRes['missing_key']:
                    self.tableMid.setRowCount(n + 1)
                    self.tableMid.setItem(n, 0, QTableWidgetItem(str(i)))
                    self.tableMid.setItem(n, 1, QTableWidgetItem('该字段缺失！'))
                    self.tableMid.item(n, 0).setBackground(
                        QBrush(QColor(255, 0, 0)))
                    self.tableMid.item(n, 1).setBackground(
                        QBrush(QColor(255, 0, 0)))
                    n += 1
                # QStandardItem()
                self.tableMid.setSortingEnabled(True)
                self.tableMid.sortByColumn(0, Qt.AscendingOrder)

        except Exception as e:
            self.logger.error(str(e))

    def tableMidCellClicked(self, row):
        """
        点击tableMid每行数据触发，如果是JSON则解析在tableRight展示
        :param row: int
        :return: None
        """
        self.tableRight.clearContents()
        tmp = self.tableMid.item(row, 1).text()
        pattern = r'^{.*}$'
        if re.match(pattern, tmp):
            extra_data = json.loads(tmp)
            n = 0
            for k in extra_data:
                self.tableRight.setRowCount(n + 1)
                self.tableRight.setItem(n, 0, QTableWidgetItem(str(k)))
                self.tableRight.setItem(n, 1, QTableWidgetItem(str(extra_data[k])))
                n += 1

    def stopSignalReceived(self, text):
        """
        子线程结束触发提示
        :param text: str
        :return:
        """
        global startFlag

        self.comboBox.setEnabled(True)
        self.btnRefresh.setEnabled(True)
        self.lineEditCmdBeforeStart.setEnabled(True)
        self.lineEditCmdAfterStop.setEnabled(True)
        self.btnStart.setEnabled(True)
        self.btnStop.setEnabled(False)
        startFlag = False
        QMessageBox.information(self, '提示', text, QMessageBox.Ok)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = LogCheckUI()
    qssstyle = '''
        .QTableWidget {
            border:1px solid #8f8f91;
            margin-left:5px;
            margin-right:5px;
            margin-bottom:5px;
        }
        .QComboBox {
            border:1px solid #8f8f91;
            border-radius:4px;
            position:relative;
            max-width:100px;
        }
        .QPushButton#btnRefresh {
            border:1px solid #8f8f91;
            border-radius:4px;
            position:relative;
            margin-left:5px;
            max-width:80px;
        }
        .QPushButton#btnClearCells {
            border:1px solid #8f8f91;
            border-radius:4px;
            position:relative;
            margin-left:5px;
            max-width:80px;
        }
        .QPushButton#btnStart {
            border:1px solid #8f8f91;
            border-radius:4px;
            position:relative;
            margin-right:5px;
            margin-left:5px;
        }
        .QPushButton#btnStop {
            border:1px solid #8f8f91;
            border-radius:4px;
            position:relative;
            margin-right:5px;
            margin-left:5px;
        }
        .QLineEdit#lineEditCmdBeforeStart {
            border:1px solid #8f8f91;
            border-radius:4px;
            margin-left:5px;
            margin-right:5px;
            width:200px;
        }
        .QLineEdit#lineEditCmdAfterStop {
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
