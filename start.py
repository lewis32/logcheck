#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable-msg=invalid-name,global-statement,typo

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from core.log_check import *
from core.package.myserial import *
from core.package.myssh import MySsh as Ssh
from core.package.myconfig import LoadConfig
from core.package.mylogging import MyLogging as Logging

CONFIG = LoadConfig().get_config()
THREAD_START_FLAG = False
SERIAL_LIST = []
CURRENT_SERIAL = None


class WorkThread(QThread):
    """
    子线程，轮询验证结果返回
    """
    add = pyqtSignal(list)
    terminal = pyqtSignal(object)
    logger = Logging(__name__)

    def run(self):
        global CONFIG, CURRENT_SERIAL, THREAD_START_FLAG

        if not CURRENT_SERIAL:
            return

        try:
            self.serial = TVSerial(port=CURRENT_SERIAL, baudrate=115200, timeout=5)
        except Exception as e:
            self.terminal.emit(str(e))
        else:
            self.serial.sendComand('\n\n')
            self.sleep(1)
            self.serial.sendComand(CONFIG.start_cmd)
            self.serial.sendComand('\n\n')
            self.sleep(1)

            self.serial.s.flushOutput()
            self.serial.s.flushInput()

            THREAD_START_FLAG = True

            self.lc = LogCheck()
            while True:
                if not THREAD_START_FLAG:
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


class LogCheckUI(QTabWidget):
    """
    UI主线程
    """

    def __init__(self):
        """
        初始化整体UI
        :return: None
        """
        global CONFIG

        super().__init__()
        self.logger = Logging(__name__)
        self.workThread = WorkThread()
        self.row = 0

        self.setWindowTitle('日志验证工具')
        self.resize(1200, 700)
        self.setFixedSize(self.width(), self.height())

        self.font = QFont()
        self.font.setPointSize(10)
        self.font.setFamily("Microsoft YaHei UI")
        self.setFont(self.font)

        self.tabMainUI = QWidget()
        self.tabEditUI = QWidget()
        self.tabHintUI = QWidget()
        self.addTab(self.tabMainUI, '日志验证')
        self.addTab(self.tabEditUI, '规则编辑')
        self.addTab(self.tabHintUI, '使用说明')
        self.initMainUI()
        self.initHintUI()
        self.bind()
        self.loadConfig()

    def initMainUI(self):
        """
        初始化主UI
        :return: None
        """
        global CONFIG

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(20, 20, 20, 20)

        # 创建串口模式header
        self.hboxLayoutSerialHeader = QHBoxLayout()
        self.hboxLayoutModeSelectHeader = QHBoxLayout()
        self.hboxLayoutModeSelectHeader.setContentsMargins(10, 0, 850, 8)
        self.radioBtnSerialMode = QRadioButton('串口模式')
        self.radioBtnKafkaMode = QRadioButton('Kafka模式')
        self.radioBtnManualMode = QRadioButton('手动模式')
        self.hboxLayoutModeSelectHeader.addWidget(self.radioBtnSerialMode)
        self.hboxLayoutModeSelectHeader.addWidget(self.radioBtnKafkaMode)
        self.hboxLayoutModeSelectHeader.addWidget(self.radioBtnManualMode)

        self.gridLayoutSerialHeader = QGridLayout()
        self.gridLayoutSerialHeader.setContentsMargins(10, 10, 10, 10)
        self.gridLayoutSerialHeader.setObjectName('hboxLayoutHeader')
        self.gridLayoutSerialCmdHeader = QGridLayout()
        self.gridLayoutSerialCmdHeader.setContentsMargins(15, 15, 15, 15)
        self.gridLayoutSerialCmdHeader.setObjectName('hboxLayoutHeader')

        self.comboBoxSerial = QComboBox()
        self.comboBoxSerial.setObjectName('comboBoxSerial')
        self.comboBoxSerial.setCurrentIndex(-1)
        self.btnSerialRefresh = QPushButton('刷新')
        self.btnSerialRefresh.setObjectName('btnHeader')
        self.btnSerialRefresh.setFixedSize(90, 25)
        self.btnSerialClear = QPushButton('清空')
        self.btnSerialClear.setObjectName('btnHeader')
        self.btnSerialClear.setFixedSize(90, 25)
        self.btnSerialTest = QPushButton('模拟调试')
        self.btnSerialTest.setObjectName('btnHeader')
        self.btnSerialTest.setFixedSize(90, 25)
        self.btnSerialTest.setVisible(False)
        self.btnSerial2Manual = QPushButton('切换手动')
        self.btnSerial2Manual.setObjectName('btnHeader')
        self.btnSerial2Manual.setFixedSize(90, 25)
        self.btnSerial2Kafka = QPushButton('切换Kafka')
        self.btnSerial2Kafka.setObjectName('btnHeader')
        self.btnSerial2Kafka.setFixedSize(90, 25)

        self.labelCmdBeforeStart = QLabel('开始前执行命令')
        self.lineEditCmdBeforeStart = QLineEdit()
        self.lineEditCmdBeforeStart.setObjectName('lineEditCmdBeforeStart')
        self.labelCmdAfterStop = QLabel('结束后执行命令')
        self.lineEditCmdAfterStop = QLineEdit()
        self.lineEditCmdAfterStop.setReadOnly(True)
        self.lineEditCmdAfterStop.setObjectName('lineEditCmdAfterStop')
        self.lineEditCmdBeforeStart.setText(CONFIG.start_cmd)
        self.lineEditCmdAfterStop.setText(CONFIG.stop_cmd)

        self.btnSerialStart = QPushButton('开始')
        self.btnSerialStart.setObjectName('btnFooter')
        self.btnSerialStart.setFont(self.font)
        self.btnSerialStop = QPushButton('停止')
        self.btnSerialStop.setObjectName('btnFooter')
        self.btnSerialStop.setFont(self.font)
        self.btnSerialStop.setEnabled(False)

        self.gridLayoutSerialCmdHeader.addWidget(self.labelCmdBeforeStart, 0, 0)
        self.gridLayoutSerialCmdHeader.addWidget(self.lineEditCmdBeforeStart, 0, 1)
        self.gridLayoutSerialCmdHeader.addWidget(self.btnSerialStart, 0, 2)
        self.gridLayoutSerialCmdHeader.addWidget(self.labelCmdAfterStop, 1, 0)
        self.gridLayoutSerialCmdHeader.addWidget(self.lineEditCmdAfterStop, 1, 1)
        self.gridLayoutSerialCmdHeader.addWidget(self.btnSerialStop, 1, 2)
        self.gridLayoutSerialHeader.addWidget(self.comboBoxSerial, 0, 0)
        self.gridLayoutSerialHeader.addWidget(self.btnSerialTest, 1, 0)
        self.gridLayoutSerialHeader.addWidget(self.btnSerialRefresh, 0, 1)
        self.gridLayoutSerialHeader.addWidget(self.btnSerialClear, 1, 1)
        self.gridLayoutSerialHeader.addWidget(self.btnSerial2Kafka, 0, 2)
        self.gridLayoutSerialHeader.addWidget(self.btnSerial2Manual, 1, 2)

        self.groupBoxSerialHeader = QGroupBox('选择端口')
        self.groupBoxSerialHeader.setObjectName('groupBoxHeader')
        self.groupBoxSerialHeader.setLayout(self.gridLayoutSerialHeader)
        self.groupBoxSerialHeader.setFixedSize(420, 120)
        self.groupBoxSerialCmdHeader = QGroupBox(r'输入命令')
        self.groupBoxSerialCmdHeader.setLayout(self.gridLayoutSerialCmdHeader)
        self.groupBoxSerialCmdHeader.setFixedSize(730, 120)
        self.hboxLayoutSerialHeader.addWidget(self.groupBoxSerialHeader)
        self.hboxLayoutSerialHeader.addWidget(self.groupBoxSerialCmdHeader)

        # 创建Kafka模式header
        self.hboxLayoutKafkaHeader = QHBoxLayout()
        self.gridLayoutSshHeader = QGridLayout()
        self.gridLayoutSshHeader.setContentsMargins(10, 10, 10, 10)
        self.gridLayoutKafkaHeader = QGridLayout()
        self.gridLayoutKafkaHeader.setContentsMargins(10, 10, 10, 10)

        self.labelSshHost = QLabel('Host')
        self.lineEditSshHost = QLineEdit()
        self.labelSshPort = QLabel('Port')
        self.lineEditSshPort = QLineEdit()
        self.labelSshUser = QLabel('User')
        self.lineEditSshUser = QLineEdit()
        self.labelSshPwd = QLabel('Pwd')
        self.lineEditSshPwd = QLineEdit()
        self.labelKafkaCluster = QLabel('Server')
        self.labelKafkaCluster.setObjectName('labelKafkaCluster')
        self.labelKafkaCluster.setAlignment(Qt.AlignRight)
        self.lineEditKafkaCluster = QLineEdit()
        self.lineEditKafkaCluster.setObjectName('lineEditKafkaCluster')
        self.lineEditKafkaCluster.setFixedSize(150, 25)
        self.labelKafkaTopic = QLabel('Topic')
        self.labelKafkaTopic.setObjectName('labelKafkaTopic')
        self.labelKafkaTopic.setAlignment(Qt.AlignRight)
        self.comboBoxKafkaTopic = QComboBox()
        self.comboBoxKafkaTopic.setObjectName('comboBoxKafkaTopic')
        self.labelKafkaFilter = QLabel('Filter')
        self.labelKafkaFilter.setObjectName('labelKafkaFilter')
        self.labelKafkaFilter.setAlignment(Qt.AlignRight)
        self.lineEditKafkaFilter = QLineEdit()
        self.checkBoxKafkaSshEnable = QCheckBox('启用SSH')
        self.checkBoxKafkaSshEnable.setObjectName('checkBoxKafkaSshEnable')
        self.btnKafkaStart = QPushButton('开始')
        self.btnKafkaStart.setObjectName('btnHeader')
        self.btnKafkaStop = QPushButton('停止')
        self.btnKafkaStop.setObjectName('btnHeader')
        self.btnKafka2Manual = QPushButton('切换手动')
        self.btnKafka2Manual.setObjectName('btnHeader')
        self.btnKafka2Serial = QPushButton('切换串口')
        self.btnKafka2Serial.setObjectName('btnHeader')

        self.gridLayoutSshHeader.addWidget(self.labelSshHost, 0, 0)
        self.gridLayoutSshHeader.addWidget(self.lineEditSshHost, 0, 1)
        self.gridLayoutSshHeader.addWidget(self.labelSshPort, 0, 2)
        self.gridLayoutSshHeader.addWidget(self.lineEditSshPort, 0, 3)
        self.gridLayoutSshHeader.addWidget(self.labelSshUser, 1, 0)
        self.gridLayoutSshHeader.addWidget(self.lineEditSshUser, 1, 1)
        self.gridLayoutSshHeader.addWidget(self.labelSshPwd, 1, 2)
        self.gridLayoutSshHeader.addWidget(self.lineEditSshPwd, 1, 3)
        self.gridLayoutKafkaHeader.addWidget(self.labelKafkaCluster, 0, 0)
        self.gridLayoutKafkaHeader.addWidget(self.lineEditKafkaCluster, 0, 1)
        self.gridLayoutKafkaHeader.addWidget(self.labelKafkaTopic, 1, 0)
        self.gridLayoutKafkaHeader.addWidget(self.comboBoxKafkaTopic, 1, 1)
        self.gridLayoutKafkaHeader.addWidget(self.checkBoxKafkaSshEnable, 1, 2)
        self.gridLayoutKafkaHeader.addWidget(self.labelKafkaFilter, 0, 2)
        self.gridLayoutKafkaHeader.addWidget(self.lineEditKafkaFilter, 0, 3, 1, 4)
        self.gridLayoutKafkaHeader.addWidget(self.btnKafkaStart, 1, 3)
        self.gridLayoutKafkaHeader.addWidget(self.btnKafkaStop, 1, 4)
        self.gridLayoutKafkaHeader.addWidget(self.btnKafka2Serial, 1, 5)
        self.gridLayoutKafkaHeader.addWidget(self.btnKafka2Manual, 1, 6)

        self.groupBoxSshHeader = QGroupBox('SSH')
        self.groupBoxSshHeader.setObjectName('groupBoxHeader')
        self.groupBoxSshHeader.setLayout(self.gridLayoutSshHeader)
        self.groupBoxSshHeader.setVisible(False)
        self.groupBoxSshHeader.setFixedSize(420, 120)
        self.groupBoxKafkaHeader = QGroupBox('Kafka')
        self.groupBoxKafkaHeader.setObjectName('groupBoxHeader')
        self.groupBoxKafkaHeader.setLayout(self.gridLayoutKafkaHeader)
        self.groupBoxKafkaHeader.setVisible(False)
        self.groupBoxKafkaHeader.setFixedSize(730, 120)

        self.hboxLayoutKafkaHeader.addWidget(self.groupBoxSshHeader)
        self.hboxLayoutKafkaHeader.addWidget(self.groupBoxKafkaHeader)

        # 创建手动模式header
        self.gridLayoutManualHeader = QGridLayout()
        self.gridLayoutManualHeader.setContentsMargins(10, 10, 10, 10)

        self.textEditManual = QTextEdit()
        self.textEditManual.setObjectName('textEditManual')
        self.btnManualCheck = QPushButton('验证')
        self.btnManualCheck.setObjectName('btnHeader')
        self.btnManualClear = QPushButton('清空')
        self.btnManualClear.setObjectName('btnHeader')
        self.btnManual2Serial = QPushButton('切换串口')
        self.btnManual2Serial.setObjectName('btnHeader')
        self.btnManual2Kafka = QPushButton('切换Kafka')
        self.btnManual2Kafka.setObjectName('btnHeader')

        self.gridLayoutManualHeader.addWidget(self.textEditManual, 0, 0, 2, 1)
        self.gridLayoutManualHeader.addWidget(self.btnManualCheck, 0, 1)
        self.gridLayoutManualHeader.addWidget(self.btnManualClear, 0, 2)
        self.gridLayoutManualHeader.addWidget(self.btnManual2Serial, 1, 1)
        self.gridLayoutManualHeader.addWidget(self.btnManual2Kafka, 1, 2)

        self.groupBoxManualHeader = QGroupBox('输入日志数据')
        self.groupBoxManualHeader.setObjectName('groupBoxHeader')
        self.groupBoxManualHeader.setLayout(self.gridLayoutManualHeader)
        self.groupBoxManualHeader.setVisible(False)
        self.groupBoxManualHeader.setFixedSize(850, 120)

        # 创建显示结果数据body
        self.hboxLayoutBody = QHBoxLayout()
        self.hboxLayoutBody.setObjectName('hboxLayoutBody')
        # hboxLayoutBody.setContentsMargins(15, 15, 15, 15)
        self.hboxLayoutTableLeft = QVBoxLayout()
        self.hboxLayoutTableMid = QVBoxLayout()
        self.hboxLayoutTableRight = QVBoxLayout()

        self.tableLeft = QTableWidget(0, 6)
        self.tableLeft.setToolTip('点击查看详细结果，右键复制验证数据')
        self.tableLeft.setMouseTracking(True)
        self.tableLeft.setFont(self.font)
        self.tableLeft.setHorizontalHeaderLabels(
            [
                'src_event_code',
                'event_code',
                'event_alias',
                'result',
                'detail',
                'more_detail'
            ]
        )
        self.tableLeft.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.tableLeft.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents)
        self.tableLeft.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableLeft.setColumnHidden(4, True)
        self.tableLeft.setColumnHidden(5, True)

        self.tableMid = QTableWidget(0, 3)
        self.tableMid.setFont(self.font)
        self.tableMid.setHorizontalHeaderLabels(
            [
                'key',
                'key_alias',
                'value'
            ]
        )
        self.tableMid.verticalHeader().setVisible(False)
        self.tableMid.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.tableMid.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents)
        self.tableMid.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.tableRight = QTableWidget(0, 3)
        self.tableRight.setFont(self.font)
        self.tableRight.setHorizontalHeaderLabels(
            [
                'key',
                'key_alias',
                'value'
            ]
        )
        self.tableRight.verticalHeader().setVisible(False)
        self.tableRight.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.tableRight.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents)
        self.tableRight.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.hboxLayoutTableLeft.addWidget(self.tableLeft)
        self.hboxLayoutTableMid.addWidget(self.tableMid)
        self.hboxLayoutTableRight.addWidget(self.tableRight)

        self.groupBoxTableLeft = QGroupBox('验证结果')
        self.groupBoxTableLeft.setLayout(self.hboxLayoutTableLeft)
        self.groupBoxTableMid = QGroupBox('一级数据')
        self.groupBoxTableMid.setLayout(self.hboxLayoutTableMid)
        self.groupBoxTableRight = QGroupBox('二级数据')
        self.groupBoxTableRight.setLayout(self.hboxLayoutTableRight)
        self.hboxLayoutBody.addWidget(self.groupBoxTableLeft)
        self.hboxLayoutBody.addWidget(self.groupBoxTableMid)
        self.hboxLayoutBody.addWidget(self.groupBoxTableRight)
        self.hboxLayoutBody.setStretchFactor(self.groupBoxTableLeft, 7)
        self.hboxLayoutBody.setStretchFactor(self.groupBoxTableMid, 7)
        self.hboxLayoutBody.setStretchFactor(self.groupBoxTableRight, 5)

        self.mainLayout.addLayout(self.hboxLayoutModeSelectHeader)
        self.mainLayout.addLayout(self.hboxLayoutSerialHeader)
        self.mainLayout.addLayout(self.hboxLayoutKafkaHeader)
        self.mainLayout.addWidget(self.groupBoxManualHeader)
        self.mainLayout.addLayout(self.hboxLayoutBody)
        self.tabMainUI.setLayout(self.mainLayout)

    def loadConfig(self):
        global CONFIG

        if CONFIG.mode == 'serial':
            self.radioBtnSerialMode.setChecked(True)
        if CONFIG.mode == 'kafka':
            self.radioBtnKafkaMode.setChecked(True)
        if CONFIG.mode == 'manual':
            self.radioBtnManualMode.setChecked(True)



    def initHintUI(self):
        """
        初始化提示UI
        :return: None
        """
        self.hintLayout = QVBoxLayout()
        self.hintLayout.setContentsMargins(20, 20, 20, 20)

        self.groupBoxHint1 = QGroupBox('提示1')
        self.groupBoxHint2 = QGroupBox('提示2')

        self.hintLayout.addWidget(self.groupBoxHint1)
        self.hintLayout.addWidget(self.groupBoxHint2)
        self.tabHintUI.setLayout(self.hintLayout)

    def bind(self):
        """
        信号绑定槽函数
        :return: None
        """
        self.radioBtnSerialMode.toggled.connect(
            lambda: self.radioBtnModeToggled(self.radioBtnSerialMode))
        self.radioBtnKafkaMode.toggled.connect(
            lambda: self.radioBtnModeToggled(self.radioBtnKafkaMode))
        self.radioBtnManualMode.toggled.connect(
            lambda: self.radioBtnModeToggled(self.radioBtnManualMode))
        self.comboBoxSerial.currentIndexChanged.connect(self.comboBoxSelected)
        self.btnSerialRefresh.clicked.connect(
            lambda: self.btnRefreshClicked(self.btnSerialRefresh))
        self.btnSerialClear.clicked.connect(
            lambda: self.btnClearClicked(self.btnSerialClear))
        self.btnSerialStart.clicked.connect(self.btnSerialStartClicked)
        self.btnSerialStop.clicked.connect(
            lambda: self.btnSerialStopClicked(self.btnSerialStop))
        self.btnSerialTest.clicked.connect(
            lambda: self.btnSerialTestClicked(self.btnSerialTest))
        self.btnSerial2Manual.clicked.connect(
            lambda: self.btnSwitchManualClicked(self.btnSerial2Manual))
        self.btnSerial2Kafka.clicked.connect(
            lambda: self.btnSwitchKafkaClicked(self.btnSerial2Kafka))
        self.lineEditCmdBeforeStart.textChanged.connect(
            lambda: self.lineEditCmdChanged(self.lineEditCmdBeforeStart))
        self.lineEditCmdAfterStop.textChanged.connect(
            lambda: self.lineEditCmdChanged(self.lineEditCmdAfterStop))
        self.tableLeft.cellClicked.connect(self.tableLeftCellClicked)
        self.tableMid.cellClicked.connect(self.tableMidCellClicked)
        self.btnKafka2Manual.clicked.connect(
            lambda: self.btnSwitchManualClicked(self.btnKafka2Manual))
        self.btnKafka2Serial.clicked.connect(
            lambda: self.btnSwitchSerialClicked(self.btnKafka2Serial))
        self.checkBoxKafkaSshEnable.stateChanged.connect(
            lambda: self.checkBoxKafkaSshEnableChanged(self.checkBoxKafkaSshEnable))
        self.btnManual2Serial.clicked.connect(
            lambda: self.btnSwitchSerialClicked(self.btnManual2Serial))
        self.btnManual2Kafka.clicked.connect(
            lambda: self.btnSwitchKafkaClicked(self.btnManual2Kafka))
        self.btnManualCheck.clicked.connect(
            lambda: self.btnManualCheckClicked(self.btnManualCheck))
        self.btnManualClear.clicked.connect(
            lambda: self.btnManualClearClicked(self.btnManualClear))

        self.workThread.add.connect(self.checkResultReceived)
        self.workThread.terminal.connect(self.stopSignalReceived)

    def radioBtnModeToggled(self, i):
        """
        选择手动模式
        :param i: object
        :return: None
        """
        global CONFIG

        if i.text() == '串口模式':
            self.groupBoxSerialHeader.setVisible(True)
            self.groupBoxSerialCmdHeader.setVisible(True)
            self.groupBoxSshHeader.setVisible(False)
            self.groupBoxKafkaHeader.setVisible(False)
            self.groupBoxManualHeader.setVisible(False)
            CONFIG.mode = 'serial'
            CONFIG.
        if i.text() == 'Kafka模式':
            self.groupBoxSerialHeader.setVisible(False)
            self.groupBoxSerialCmdHeader.setVisible(False)
            self.groupBoxSshHeader.setVisible(True)
            self.groupBoxKafkaHeader.setVisible(True)
            self.groupBoxManualHeader.setVisible(False)
            CONFIG.mode = 'kafka'
        if i.text() == '手动模式':
            self.groupBoxSerialHeader.setVisible(False)
            self.groupBoxSerialCmdHeader.setVisible(False)
            self.groupBoxSshHeader.setVisible(False)
            self.groupBoxKafkaHeader.setVisible(False)
            self.groupBoxManualHeader.setVisible(True)
            CONFIG.mode = 'manual'

    def comboBoxSelected(self, i):
        """
        下拉框选择端口触发
        :param i: object
        :return: None
        """
        global CURRENT_SERIAL

        self.logger.info("Text in combobox: " + self.comboBoxSerial.currentText())

        if self.comboBoxSerial.currentText():
            CURRENT_SERIAL = re.findall(
                r'COM[0-9]+', self.comboBoxSerial.currentText())[0]

    def lineEditCmdChanged(self, i):
        """
        修改执行命令触发
        :param i: object
        :return: None
        """
        global CONFIG

        if self.lineEditCmdBeforeStart.text():
            CONFIG.start_cmd = self.lineEditCmdBeforeStart.text()
        if self.lineEditCmdAfterStop.text():
            CONFIG.stop_cmd = self.lineEditCmdAfterStop.text()

    def btnRefreshClicked(self, btn):
        """
        点击刷新按钮触发
        :param btn: object
        :return: None
        """
        self.comboBoxSerial.clear()
        try:
            portList = getPortList()
        except Exception as e:
            self.logger.error("Error occurs while get port list: " + str(e))
            QMessageBox.information(self, '提示', str(e), QMessageBox.Ok)
        else:
            if portList:
                for i in portList:
                    try:
                        self.comboBoxSerial.addItem(i[0])
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

    def btnSerialStartClicked(self, btn):
        """
        点击开始按钮触发
        :param btn: object
        :return: None
        """
        try:
            global THREAD_START_FLAG

            if not CURRENT_SERIAL:
                QMessageBox.information(self, '提示', '请先选择端口！',
                    QMessageBox.Ok)
                return

            self.row = 0
            self.tableLeft.clearContents()
            self.tableMid.clearContents()
            self.tableRight.clearContents()
            self.workThread.start()

            self.comboBoxSerial.setEnabled(False)
            self.btnSerialRefresh.setEnabled(False)
            self.lineEditCmdBeforeStart.setEnabled(False)
            self.lineEditCmdAfterStop.setEnabled(False)
            self.btnSerialStart.setEnabled(False)
            self.btnSerialStop.setEnabled(False)

            # 开始后马上点击结束会报错，添加延时
            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: self.btnSerialStop.setEnabled(True))
            timer.start(5000)
            timer.start(5000)
        except Exception as e:
            print(str(e))

    def btnSerialStopClicked(self, btn):
        """
        点击结束按钮触发
        :param btn: object
        :return: None
        """
        global CONFIG, THREAD_START_FLAG

        if not THREAD_START_FLAG:
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

        self.comboBoxSerial.setEnabled(True)
        self.btnSerialRefresh.setEnabled(True)
        self.lineEditCmdBeforeStart.setEnabled(True)
        self.lineEditCmdAfterStop.setEnabled(True)
        self.btnSerialStart.setEnabled(True)
        self.btnSerialStop.setEnabled(False)
        THREAD_START_FLAG = False

    def checkResultReceived(self, res):
        """
        获得检验结果返回触发
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
            self.tableLeft.setItem(self.row, 2, QTableWidgetItem(
                str(i['event_alias']) if i['event_alias'] else 'N/A'))

            if i['result'] == -1:
                self.tableLeft.setItem(self.row, 3, QTableWidgetItem('N/A'))
                # 灰色表示从配置文件中找不到对应的事件
                self.tableLeft.item(self.row, 3).setBackground(
                    QBrush(QColor(211, 211, 211)))
                self.setToolTip('配置文件中没有对应的eventcode！')
            if i['result'] == 0:
                self.tableLeft.setItem(self.row, 3, QTableWidgetItem('Pass'))
                # 绿色表示全部字段均正常
                self.tableLeft.item(self.row, 3).setBackground(
                    QBrush(QColor(0, 128, 0)))
                # fontLight = QFont()
                # fontLight.setStyle()
                # self.tableLeft.item(self.row, 2).setFont(QFont(QFont="White"))
                self.setToolTip('所有字段均正常，Ctrl+C可复制内容')
            if i['result'] == 1:
                self.tableLeft.setItem(self.row, 3, QTableWidgetItem('Fail'))
                # 红色表示部分字段缺失或值错误
                self.tableLeft.item(self.row, 3).setBackground(
                    QBrush(QColor(255, 0, 0)))
                self.setToolTip('部分字段缺失或错误，Ctrl+C可复制内容')
            if i['result'] == 2:
                self.tableLeft.setItem(self.row, 3,
                                       QTableWidgetItem('Warn'))
                # 黄色表示包含未定义字段
                self.tableLeft.item(self.row, 3).setBackground(
                    QBrush(QColor(255, 255, 0)))
                self.setToolTip('部分字段不在定义内，Ctrl+C可复制内容')

            # self.table1.setItem(self.row, 2, QTableWidgetItem(
            #     'Fail' if i['result'] else 'Pass'))
            self.tableLeft.setItem(self.row, 4, QTableWidgetItem(
                json.dumps(i['data'])))
            self.tableLeft.setItem(self.row, 5, QTableWidgetItem(
                json.dumps(i)))

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

            if self.tableLeft.item(row, 4) and self.tableLeft.item(row, 5):
                self.tableMid.setSortingEnabled(False)
                dictData = json.loads(self.tableLeft.item(row, 4).text())
                dictRes = json.loads(self.tableLeft.item(row, 5).text())
                n = 0
                # for k in dictData:
                for k in dictRes['data']:
                    self.tableMid.setRowCount(n + 1)
                    self.tableMid.setItem(n, 0, QTableWidgetItem(str(k)))
                    self.tableMid.setItem(n, 1, QTableWidgetItem(str(dictRes['data'][k].get('key_alias'))))
                    self.tableMid.setItem(n, 2, QTableWidgetItem(str(dictRes['data'][k].get('value'))))

                    if k in dictRes['invalid_key']:
                        self.tableMid.item(n, 0).setBackground(
                            QBrush(QColor(255, 0, 0)))
                        self.tableMid.item(n, 1).setBackground(
                            QBrush(QColor(255, 0, 0)))
                        self.tableMid.item(n, 2).setBackground(
                            QBrush(QColor(255, 0, 0)))

                    if k in dictRes['undefined_key']:
                        self.tableMid.item(n, 0).setBackground(
                            QBrush(QColor(255, 255, 0)))
                        self.tableMid.item(n, 1).setBackground(
                            QBrush(QColor(255, 255, 0)))
                        self.tableMid.item(n, 2).setBackground(
                            QBrush(QColor(255, 255, 0)))
                    n += 1

                for i in dictRes['missing_key']:
                    self.tableMid.setRowCount(n + 1)
                    self.tableMid.setItem(n, 0, QTableWidgetItem(str(i)))
                    self.tableMid.setItem(n, 1, QTableWidgetItem(str(dictRes['missing_key'][i].get('key_alias'))))
                    self.tableMid.setItem(n, 2, QTableWidgetItem('该字段缺失！'))
                    self.tableMid.item(n, 0).setBackground(
                        QBrush(QColor(255, 0, 0)))
                    self.tableMid.item(n, 1).setBackground(
                        QBrush(QColor(255, 0, 0)))
                    self.tableMid.item(n, 2).setBackground(
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
        tmp = self.tableMid.item(row, 2).text()
        pattern = r'^{.*}$'
        if re.match(pattern, tmp):
            extra_data = json.loads(tmp)
            n = 0
            for k in extra_data:
                self.tableRight.setRowCount(n + 1)
                self.tableRight.setItem(n, 0, QTableWidgetItem(str(k)))
                self.tableRight.setItem(n, 1, QTableWidgetItem())
                self.tableRight.setItem(n, 2, QTableWidgetItem(str(extra_data[k])))
                n += 1

    def stopSignalReceived(self, text):
        """
        子线程结束触发提示
        :param text: str
        :return:
        """
        global THREAD_START_FLAG

        self.comboBoxSerial.setEnabled(True)
        self.btnSerialRefresh.setEnabled(True)
        self.lineEditCmdBeforeStart.setEnabled(True)
        self.lineEditCmdAfterStop.setEnabled(True)
        self.btnSerialStart.setEnabled(True)
        self.btnSerialStop.setEnabled(False)
        THREAD_START_FLAG = False
        QMessageBox.information(self, '提示', text, QMessageBox.Ok)

    def btnSerialTestClicked(self, i):
        """
        点击自动模式的模拟调试按钮
        :param i: object
        :return: None
        """
        data = """{   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "eventcode" : "211010",   "eventtime" : "1585185206",   "logstamp" : "21",   "os" : "Linux",   "pageid" : "home",   "pagetype" : "-1",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"},{   "appid" : "184",   "appname" : "vidaa-free",   "apppackage" : "vidaa-free",   "appversion" : "",   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "endtime" : "0",   "eventcode" : "200101",   "launchsource" : "1",   "os" : "Linux",   "starttime" : "1585185206",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"},{   "backgroundapppackage" : "launcher",   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "closereason" : "1",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "endtime" : "1585185206",   "eventcode" : "200147",   "os" : "Linux",   "starttime" : "1585185203",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"},{   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "columnid" : "341",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "eventcode" : "211011",   "eventtime" : "1585185230",   "logstamp" : "21",   "objectid" : "68",   "objecttype" : "600003",   "original" : "0",   "os" : "Linux",   "pageid" : "home",   "pagetype" : "-1",   "posindex" : "0",   "rowindex" : "9",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"}
,{   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "eventcode" : "200242",   "eventtime" : "1585185126",   "os" : "Linux",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"},{   "backgroundapppackage" : "launcher",   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "closereason" : "0",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "endtime" : "0",   "eventcode" : "200147",   "os" : "Linux",   "starttime" : "1585185181",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"},{   "backgroundapppackage" : "launcher",   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "closereason" : "1",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "endtime" : "1585185184",   "eventcode" : "200147",   "os" : "Linux",   "starttime" : "1585185181",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"},{   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "eventcode" : "200120",   "eventtime" : "1585185188",   "keyname" : "TWO",   "os" : "Linux",   "remotecontroltype" : "EN3B39",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"},{   "backgroundapppackage" : "launcher",   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "closereason" : "0",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "endtime" : "0",   "eventcode" : "200147",   "os" : "Linux",   "starttime" : "1585185189",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"},{   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "columnid" : "navigation",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "eventcode" : "200291",   "eventtime" : "1585185192",   "objectid" : "setting",   "objecttype" : "9900",   "original" : "-1",   "os" : "Linux",   "pageid" : "launcher",   "pagetype" : "-1",   "posindex" : "2",   "rowindex" : "0",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"},{   "backgroundapppackage" : "launcher",   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "closereason" : "1",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "endtime" : "1585185192",   "eventcode" : "200147",   "os" : "Linux",   "starttime" : "1585185189",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"},{   "backgroundapppackage" : "launcher",   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "closereason" : "0",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "endtime" : "0",   "eventcode" : "200147",   "os" : "Linux",   "starttime" : "1585185198",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"},{   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "columnid" : "navigation",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "eventcode" : "200291",   "eventtime" : "1585185200",   "objectid" : "notification",   "objecttype" : "9900",   "original" : "-1",   "os" : "Linux",   "pageid" : "launcher",   "pagetype" : "-1",   "posindex" : "3",   "rowindex" : "0",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"},{   "backgroundapppackage" : "launcher",   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "closereason" : "1",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "endtime" : "1585185200",   "eventcode" : "200147",   "os" : "Linux",   "starttime" : "1585185198",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"},{   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "eventcode" : "200260",   "eventtime" : "1585185201",   "objectid" : "setting",   "objecttype" : "9900",   "os" : "Linux",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"},{   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "eventcode" : "200261",   "eventtime" : "1585185202",   "extra" : "{\"advertising\":1,\"newarrivals\":1,\"warningsandlegalstatements\":1,\"systemmessage\":1}",   "os" : "Linux",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"},{   "backgroundapppackage" : "launcher",   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "closereason" : "0",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "endtime" : "0",   "eventcode" : "200147",   "os" : "Linux",   "starttime" : "1585185203",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"}"""
        self.logger.info('Mock log data: ' + data)
        self.test = LogCheck()
        res = self.test.check_log(data)
        if res:
            self.row = 0
            self.checkResultReceived(res)
        self.logger.info('Mock Check result: ' + str(res))

    def btnManualCheckClicked(self, i):
        """
        点击手动模式的验证按钮
        :param i: object
        :return: None
        """
        try:
            data_tmp = """{   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "eventcode" : "211010",   "eventtime" : "1585185206",   "logstamp" : "21",   "os" : "Linux",   "pageid" : "home",   "pagetype" : "-1",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"},{   "appid" : "184",   "appname" : "vidaa-free",   "apppackage" : "vidaa-free",   "appversion" : "",   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "endtime" : "0",   "eventcode" : "200101",   "launchsource" : "1",   "os" : "Linux",   "starttime" : "1585185206",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"},{   "backgroundapppackage" : "launcher",   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "closereason" : "1",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "endtime" : "1585185206",   "eventcode" : "200147",   "os" : "Linux",   "starttime" : "1585185203",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"},{   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "columnid" : "341",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "eventcode" : "211011",   "eventtime" : "1585185230",   "logstamp" : "21",   "objectid" : "68",   "objecttype" : "600003",   "original" : "0",   "os" : "Linux",   "pageid" : "home",   "pagetype" : "-1",   "posindex" : "0",   "rowindex" : "9",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"}
            ,{   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "eventcode" : "200242",   "eventtime" : "1585185126",   "os" : "Linux",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"},{   "backgroundapppackage" : "launcher",   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "closereason" : "0",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "endtime" : "0",   "eventcode" : "200147",   "os" : "Linux",   "starttime" : "1585185181",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"},{   "backgroundapppackage" : "launcher",   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "closereason" : "1",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "endtime" : "1585185184",   "eventcode" : "200147",   "os" : "Linux",   "starttime" : "1585185181",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"},{   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "eventcode" : "200120",   "eventtime" : "1585185188",   "keyname" : "TWO",   "os" : "Linux",   "remotecontroltype" : "EN3B39",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"},{   "backgroundapppackage" : "launcher",   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "closereason" : "0",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "endtime" : "0",   "eventcode" : "200147",   "os" : "Linux",   "starttime" : "1585185189",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"},{   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "columnid" : "navigation",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "eventcode" : "200291",   "eventtime" : "1585185192",   "objectid" : "setting",   "objecttype" : "9900",   "original" : "-1",   "os" : "Linux",   "pageid" : "launcher",   "pagetype" : "-1",   "posindex" : "2",   "rowindex" : "0",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"},{   "backgroundapppackage" : "launcher",   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "closereason" : "1",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "endtime" : "1585185192",   "eventcode" : "200147",   "os" : "Linux",   "starttime" : "1585185189",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"},{   "backgroundapppackage" : "launcher",   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "closereason" : "0",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "endtime" : "0",   "eventcode" : "200147",   "os" : "Linux",   "starttime" : "1585185198",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"},{   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "columnid" : "navigation",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "eventcode" : "200291",   "eventtime" : "1585185200",   "objectid" : "notification",   "objecttype" : "9900",   "original" : "-1",   "os" : "Linux",   "pageid" : "launcher",   "pagetype" : "-1",   "posindex" : "3",   "rowindex" : "0",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"},{   "backgroundapppackage" : "launcher",   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "closereason" : "1",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "endtime" : "1585185200",   "eventcode" : "200147",   "os" : "Linux",   "starttime" : "1585185198",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"},{   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "eventcode" : "200260",   "eventtime" : "1585185201",   "objectid" : "setting",   "objecttype" : "9900",   "os" : "Linux",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"},{   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "eventcode" : "200261",   "eventtime" : "1585185202",   "extra" : "{\"advertising\":1,\"newarrivals\":1,\"warningsandlegalstatements\":1,\"systemmessage\":1}",   "os" : "Linux",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"},{   "backgroundapppackage" : "launcher",   "brand" : "his",   "capabilitycode" : "2019072901",   "chipplatform" : "mstar6886",   "closereason" : "0",   "countrycode" : "GBR",   "deviceid" : "861003009000006000000641f432adfa1fb7ee6860d2ed6cf6eb0d9a",   "devicemsg" : "HE55A6103FUWTS351",   "endtime" : "0",   "eventcode" : "200147",   "os" : "Linux",   "starttime" : "1585185203",   "tvmode" : "2",   "tvversion" : "V0000.01.00G.K0324",   "version" : "3.0",   "zone" : "0"}"""
            print(self.textEditManual.toPlainText())
            data = self.textEditManual.toPlainText() if self.textEditManual.toPlainText().strip() \
                else data_tmp
            self.logger.info('Mock log data: ' + data)
            test = LogCheck()
            res = test.check_log(data)
            if res:
                self.row = 0
                self.checkResultReceived(res)
            self.logger.info('Mock Check result: ' + str(res))
        except Exception as e:
            print(e)

    def btnManualClearClicked(self, i):
        """
        点击手动模式的清空按钮
        :param i: object
        :return: None
        """
        self.textEditManual.clear()
        self.tableLeft.clearContents()
        self.tableMid.clearContents()
        self.tableRight.clearContents()
        self.row = 0

    def btnSwitchManualClicked(self, i):
        """
        切换手动模式
        :param i: object
        :return: None
        """
        global THREAD_START_FLAG

        try:
            self.groupBoxSerialHeader.setVisible(False)
            self.groupBoxSshHeader.setVisible(False)
            self.groupBoxKafkaHeader.setVisible(False)
            # self.groupBoxKafkaFilterHeader.setVisible(False)
            self.groupBoxSerialCmdHeader.setVisible(False)
            self.groupBoxManualHeader.setVisible(True)
            if THREAD_START_FLAG is True:
                self.workThread.wait()
            self.tableLeft.clearContents()
            self.tableMid.clearContents()
            self.tableRight.clearContents()
            self.row = 0

        except Exception as e:
            print(str(e))

    def btnSwitchSerialClicked(self, i):
        """
        切换串口模式
        :param i: object
        :return: None
        """
        global THREAD_START_FLAG

        try:
            self.groupBoxSshHeader.setVisible(False)
            self.groupBoxKafkaHeader.setVisible(False)
            # self.groupBoxKafkaFilterHeader.setVisible(False)
            self.groupBoxManualHeader.setVisible(False)
            self.groupBoxSerialCmdHeader.setVisible(True)
            self.groupBoxSerialHeader.setVisible(True)
            if THREAD_START_FLAG is True:
                self.workThread.start()
            self.tableLeft.clearContents()
            self.tableMid.clearContents()
            self.tableRight.clearContents()
            self.row = 0

        except Exception as e:
            print(str(e))

    def btnSwitchKafkaClicked(self, i):
        """
        切换Kafka模式
        :param i: object
        :return: None
        """
        global THREAD_START_FLAG

        try:
            self.groupBoxSerialHeader.setVisible(False)
            self.groupBoxManualHeader.setVisible(False)
            self.groupBoxSerialCmdHeader.setVisible(False)
            self.groupBoxSshHeader.setVisible(True)
            self.groupBoxKafkaHeader.setVisible(True)
            # self.groupBoxKafkaFilterHeader.setVisible(True)
            if THREAD_START_FLAG is True:
                self.workThread.start()
            self.tableLeft.clearContents()
            self.tableMid.clearContents()
            self.tableRight.clearContents()
            self.row = 0

        except Exception as e:
            print(str(e))

    def btnKafkaSshConnectClicked(self, i):
        """
        点击SSH连接按钮
        :param i: object
        :return: None
        """
        global ssh_host, ssh_port, ssh_user, ssh_pwd

        try:
            ssh_host = self.lineEditSshHost.text()
            ssh_port = self.lineEditSshPort.text()
            ssh_user = self.lineEditSshUser.text()
            ssh_pwd = self.lineEditSshPwd.text()

            self.session = Ssh(ssh_host, int(ssh_port), ssh_user, ssh_pwd, '192.169.1.181', 9092)
            self.session.start()

        except Exception as e:
            self.logger.error(str(e))
            QMessageBox.information(self, '提示', str(e),
                                    QMessageBox.Ok)

    def checkBoxKafkaSshEnableChanged(self, i):
        """
        SSH启用状态修改
        :param i: object
        :return: None
        """
        if not self.checkBoxKafkaSshEnable.checkState():
            self.groupBoxSshHeader.setEnabled(False)
        else:
            self.groupBoxSshHeader.setEnabled(True)


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
        .QLabel#labelKafkaCluster {
            height:25px;
            position:relative;
            max-width:100px;
        }
        .QLabel#labelKafkaTopic {
            height:25px;
            position:relative;
            max-width:100px;
        }
        .QLabel#labelKafkaFilter {
            height:25px;
            position:relative;
            max-width:80px;
        }        
        .QComboBox#comboBoxSerial {
            border:1px solid #8f8f91;
            width:150px;
            height:25px;
            position:relative;
            max-width:200px;
        }
        .QComboBox#comboBoxKafkaTopic {
            border:1px solid #8f8f91;
            width:150px;
            height:25px;
            position:relative;
            max-width:200px;
        }
        .QCheckBox#checkBoxKafkaSshEnable {
            margin-left:10px;
        }
        .QPushButton#btnHeader {
            border:1px solid #8f8f91;
            width:90px;
            height:25px;
            border-radius:4px;
            position:relative;
            margin-left:5px;
            max-width:80px;
        }
        .QPushButton#btnFooter {
            border:1px solid #8f8f91;
            width:70px;
            height:25px;
            border-radius:4px;
            position:relative;
            margin-left:5px;
            max-width:80px;
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
        .QLineEdit#lineEditKafkaCluster {
            border:1px solid #8f8f91;
            //border-radius:4px;
            margin-left:5px;
            margin-right:5px;
            width:10px;
            height:25px;
        }
        .QTextEdit#textEditManual {
            border:1px solid #8f8f91;
            border-radius:4px;
            margin-left:5px;
            margin-right:5px;
            width:100px;
        }
    '''
    main.setStyleSheet(qssstyle)
    main.show()
    sys.exit(app.exec_())
