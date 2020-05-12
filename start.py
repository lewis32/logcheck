#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable-msg=invalid-name,global-statement,typo

import sys
import socket
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from core.log_check import *
from core.package.myserial import *
from core.package.mykafka import MyKafka as Kafka
from core.package.mylogging import MyLogging as Logging
from configparser import *
from core.package.mycombobox import MyComboBox

path = os.path.abspath((os.path.dirname(os.path.realpath(__file__))))
log = Logging.getLogger('start')
config_path = os.path.join(path, 'conf', 'cfg.ini')
config = ConfigParser()
config.read(config_path)

dict_ = {
    'kafka_cur_alias': '',
    'kafka_cur_server': '',
    'kafka_cur_topic': '',
    'kafka_cur_filter': '',
    'serial_cur_com': '',
    'serial_cur_cmd': '',
    'serial_cur_filter': ''
}


class SerialThread(QThread):
    """
    串口模式子线程，轮询验证结果返回
    """
    add = pyqtSignal(list)
    terminal = pyqtSignal(object)

    def __init__(self):
        super(SerialThread, self).__init__()
        self.working = True

    def __del__(self):
        self.working = False
        self.wait()

    def run(self):
        try:
            self.serial = TVSerial(
                port=dict_['serial_cur_com'], baudrate=115200, timeout=5)
            self.serial.sendComand('\n\n')
            self.sleep(1)
            self.serial.sendComand(
                config.get(dict_['serial_cur_cmd'], 'start_cmd'))
            self.serial.sendComand('\n\n')
            self.sleep(1)

            self.serial.s.flushOutput()
            self.serial.s.flushInput()

            self.lc = LogCheck()
            while self.working:
                block = self.serial.s.read(size=10000).decode(
                        'utf-8', errors='ignore')
                if block and block.strip():
                    log.info('Original log data: ' + block)
                    log.info('Filter: ' + dict_['serial_cur_filter'])
                    res = self.lc.check_log(block, dict_['serial_cur_filter'].strip())
                    if res:
                        log.info('Check result: ' + str(res))
                        self.add.emit(res)
                self.sleep(1)
            self.terminal.emit('串口通信正常结束！')
        except Exception as e:
            log.error(str(e))
            self.terminal.emit(str(e))


class KafkaThread(QThread):
    """
    Kafka模式子线程，轮询验证结果返回
    """
    add = pyqtSignal(list)
    terminal = pyqtSignal(object)

    def __init__(self):
        super(KafkaThread, self).__init__()
        self.working = True

    def __del__(self):
        self.working = False
        self.wait()

    def run(self):
        try:
            kafka_server = {
                'server': dict_['kafka_cur_server'],
                'group_id': config.get(dict_['kafka_cur_alias'], 'group_id')
            }
            ssh_config = {
                'host': config.get(dict_['kafka_cur_alias'], 'ssh_host'),
                'port': config.get(dict_['kafka_cur_alias'], 'ssh_port'),
                'user': config.get(dict_['kafka_cur_alias'], 'ssh_user'),
                'pwd': config.get(dict_['kafka_cur_alias'], 'ssh_pwd')
            } if config.getboolean(
                dict_['kafka_cur_alias'], 'ssh_enable') else None

            self.kafka = Kafka(kafka_config=kafka_server, ssh_config=ssh_config)
            self.kafka.init_kafka()
            self.kafka.subscribe_kafka(topics=[dict_['kafka_cur_topic']])
            self.lc = LogCheck()
            log.info(self.currentThreadId())
            while self.working:
                block = self.kafka.poll_kafka()
                if block and block.strip():
                    log.info('Log data: ' + block)
                    res = self.lc.check_log(block, dict_['kafka_cur_filter'].strip())
                    if res:
                        log.info('Log check result: ' + str(res))
                        self.add.emit(res)
                self.sleep(1)
            self.terminal.emit('Kafka通信正常结束！')
        except Exception as e:
            log.error(str(e))
            self.terminal.emit(str(e))


class TabWidget(QTabWidget):
    def closeEvent(self, event):
        try:
            with open(os.path.join(path, 'conf', 'cfg.ini'), 'w') as f:
                config.write(f)
            event.accept()
        except Exception as e:
            log.error(str(e))


class LogCheckUI(TabWidget):
    """
    UI主线程
    """
    def __init__(self):
        """
        初始化整体UI
        :return: None
        """
        super().__init__()
        self.serialThread = SerialThread()
        self.kafkaThread = KafkaThread()
        self.row = 0

        self.setWindowTitle('日志验证工具 v1.3')
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
        # self.addTab(self.tabEditUI, '规则编辑')
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
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(20, 20, 20, 20)

        # 创建串口模式header
        self.hboxLayoutSerialHeader = QHBoxLayout()
        self.hboxLayoutModeSelectHeader = QHBoxLayout()
        self.hboxLayoutModeSelectHeader.setContentsMargins(10, 0, 800, 10)
        self.radioBtnSerialMode = QRadioButton('串口模式')
        self.radioBtnKafkaMode = QRadioButton('Kafka模式')
        self.radioBtnManualMode = QRadioButton('手动模式')
        self.hboxLayoutModeSelectHeader.addWidget(self.radioBtnSerialMode)
        self.hboxLayoutModeSelectHeader.addWidget(self.radioBtnKafkaMode)
        self.hboxLayoutModeSelectHeader.addWidget(self.radioBtnManualMode)

        self.gridLayoutSerialHeader = QGridLayout()
        self.gridLayoutSerialHeader.setContentsMargins(10, 10, 300, 10)
        self.gridLayoutSerialHeader.setObjectName('hboxLayoutHeader')

        self.labelSerialCom = QLabel('端口')
        self.labelSerialCom.setObjectName('labelSerialCom')
        self.comboBoxSerialCom = MyComboBox()
        self.comboBoxSerialCom.setObjectName('comboBoxSerial')
        self.comboBoxSerialCom.setCurrentIndex(-1)
        self.labelSerialFilter = QLabel('过滤词')
        self.labelSerialFilter.setObjectName('labelKafkaFilter')
        self.lineEditSerialFilter = QLineEdit()
        self.lineEditSerialFilter.setObjectName('lineEditSerialFilter')
        self.labelSerialCmd = QLabel('执行Shell命令')
        self.labelSerialCmd.setObjectName('labelSerialCmd')
        self.comboBoxSerialCmd = MyComboBox()
        self.comboBoxSerialCmd.setObjectName('comboBoxSerialCmd')
        self.btnSerialStart = QPushButton('开始')
        self.btnSerialStart.setObjectName('btnHeader')
        self.btnSerialStop = QPushButton('停止')
        self.btnSerialStop.setObjectName('btnHeader')
        self.btnSerialStop.setEnabled(False)
        self.btnSerialClear = QPushButton('清空')
        self.btnSerialClear.setObjectName('btnHeader')
        self.btnSerialTest = QPushButton('模拟调试')
        self.btnSerialTest.setObjectName('btnHeader')
        self.btnSerialTest.setVisible(True)

        self.gridLayoutSerialHeader.addWidget(self.labelSerialCom, 0, 0)
        self.gridLayoutSerialHeader.addWidget(self.comboBoxSerialCom, 0, 1)
        self.gridLayoutSerialHeader.addWidget(self.labelSerialFilter, 0, 2)
        self.gridLayoutSerialHeader.addWidget(self.lineEditSerialFilter, 0, 3, 1, 2)
        self.gridLayoutSerialHeader.addWidget(self.labelSerialCmd, 1, 0)
        self.gridLayoutSerialHeader.addWidget(self.comboBoxSerialCmd, 1, 1)
        self.gridLayoutSerialHeader.addWidget(self.btnSerialStart, 1, 2)
        self.gridLayoutSerialHeader.addWidget(self.btnSerialStop, 1, 3)
        self.gridLayoutSerialHeader.addWidget(self.btnSerialClear, 1, 4)
        self.gridLayoutSerialHeader.addWidget(self.btnSerialTest, 1, 5)

        self.groupBoxSerialHeader = QGroupBox('串口配置')
        self.groupBoxSerialHeader.setObjectName('groupBoxHeader')
        self.groupBoxSerialHeader.setLayout(self.gridLayoutSerialHeader)
        self.groupBoxSerialHeader.setFixedSize(850, 120)

        # 创建Kafka模式header
        self.hboxLayoutKafkaHeader = QHBoxLayout()
        self.gridLayoutSshHeader = QGridLayout()
        self.gridLayoutSshHeader.setContentsMargins(10, 10, 10, 10)
        self.gridLayoutKafkaHeader = QGridLayout()
        self.gridLayoutKafkaHeader.setContentsMargins(10, 10, 10, 10)

        self.labelSshHost = QLabel('主机名')
        self.labelSshHost.setObjectName('labelSshHost')
        self.lineEditSshHost = QLineEdit()
        self.lineEditSshHost.setObjectName('lineEditSshHost')
        self.labelSshPort = QLabel('端口')
        self.labelSshPort.setObjectName('labelSshPort')
        self.lineEditSshPort = QLineEdit()
        self.lineEditSshPort.setObjectName('lineEditSshPort')
        self.labelSshUser = QLabel('用户名')
        self.labelSshUser.setObjectName('labelSshUser')
        self.lineEditSshUser = QLineEdit()
        self.lineEditSshUser.setObjectName('lineEditSshUser')
        self.labelSshPwd = QLabel('密码')
        self.labelSshPwd.setObjectName('labelSshPwd')
        self.lineEditSshPwd = QLineEdit()
        self.lineEditSshPwd.setObjectName('lineEditSshPwd')
        self.labelKafkaCluster = QLabel('Server')
        self.labelKafkaCluster.setObjectName('labelKafkaCluster')
        self.comboBoxKafkaCluster = MyComboBox()
        self.comboBoxKafkaCluster.setObjectName('comboBoxKafkaCluster')
        self.labelKafkaTopic = QLabel('Topic')
        self.labelKafkaTopic.setObjectName('labelKafkaTopic')
        self.comboBoxKafkaTopic = MyComboBox()
        self.comboBoxKafkaTopic.setObjectName('comboBoxKafkaTopic')
        self.labelKafkaFilter = QLabel('过滤词')
        self.labelKafkaFilter.setObjectName('labelKafkaFilter')
        self.lineEditKafkaFilter = QLineEdit()
        self.lineEditKafkaFilter.setObjectName('lineEditKafkaFilter')
        self.checkBoxKafkaSshEnable = QCheckBox('启用SSH通道')
        self.checkBoxKafkaSshEnable.setObjectName('checkBoxKafkaSshEnable')
        self.btnKafkaStart = QPushButton('开始')
        self.btnKafkaStart.setObjectName('btnHeader')
        self.btnKafkaStop = QPushButton('停止')
        self.btnKafkaStop.setObjectName('btnHeader')
        self.btnKafkaStop.setEnabled(False)
        self.btnKafkaClear = QPushButton('清空')
        self.btnKafkaClear.setObjectName('btnHeader')

        self.gridLayoutSshHeader.addWidget(self.labelSshHost, 0, 0)
        self.gridLayoutSshHeader.addWidget(self.lineEditSshHost, 0, 1)
        self.gridLayoutSshHeader.addWidget(self.labelSshPort, 0, 2)
        self.gridLayoutSshHeader.addWidget(self.lineEditSshPort, 0, 3)
        self.gridLayoutSshHeader.addWidget(self.labelSshUser, 1, 0)
        self.gridLayoutSshHeader.addWidget(self.lineEditSshUser, 1, 1)
        self.gridLayoutSshHeader.addWidget(self.labelSshPwd, 1, 2)
        self.gridLayoutSshHeader.addWidget(self.lineEditSshPwd, 1, 3)
        self.gridLayoutKafkaHeader.addWidget(self.labelKafkaCluster, 0, 0)
        self.gridLayoutKafkaHeader.addWidget(self.comboBoxKafkaCluster, 0, 1)
        self.gridLayoutKafkaHeader.addWidget(self.labelKafkaFilter, 0, 2)
        self.gridLayoutKafkaHeader.addWidget(self.lineEditKafkaFilter, 0, 3, 1, 4)
        self.gridLayoutKafkaHeader.addWidget(self.labelKafkaTopic, 1, 0)
        self.gridLayoutKafkaHeader.addWidget(self.comboBoxKafkaTopic, 1, 1, 1, 2)
        self.gridLayoutKafkaHeader.addWidget(self.checkBoxKafkaSshEnable, 1, 3)
        self.gridLayoutKafkaHeader.addWidget(self.btnKafkaStart, 1, 4)
        self.gridLayoutKafkaHeader.addWidget(self.btnKafkaStop, 1, 5)
        self.gridLayoutKafkaHeader.addWidget(self.btnKafkaClear, 1, 6)

        self.groupBoxSshHeader = QGroupBox('SSH配置')
        self.groupBoxSshHeader.setObjectName('groupBoxHeader')
        self.groupBoxSshHeader.setLayout(self.gridLayoutSshHeader)
        self.groupBoxSshHeader.setVisible(False)
        self.groupBoxSshHeader.setFixedSize(420, 120)
        self.groupBoxKafkaHeader = QGroupBox('Kafka配置')
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

        self.gridLayoutManualHeader.addWidget(self.textEditManual, 0, 0, 2, 1)
        self.gridLayoutManualHeader.addWidget(self.btnManualClear, 0, 1)
        self.gridLayoutManualHeader.addWidget(self.btnManualCheck, 1, 1)

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
                '上级事件码',
                '本级事件码',
                '事件别名',
                '结果',
                '详情1',
                '详情2'
            ]
        )
        # self.tableLeft.horizontalHeader().setSectionResizeMode(
        #     QHeaderView.Stretch)
        self.tableLeft.horizontalHeader().setSectionResizeMode(
            QHeaderView.Fixed)
        # self.tableLeft.horizontalHeader().setSectionResizeMode(
        #     0, QHeaderView.ResizeToContents)
        self.tableLeft.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableLeft.setAlternatingRowColors(True)
        self.tableLeft.setColumnHidden(3, True)
        self.tableLeft.setColumnHidden(4, True)
        self.tableLeft.setColumnHidden(5, True)
        self.tableLeft.setColumnWidth(0, 80)
        self.tableLeft.setColumnWidth(1, 80)
        self.tableLeft.setColumnWidth(2, 155)

        self.tableMid = QTableWidget(0, 5)
        self.tableMid.setFont(self.font)
        self.tableMid.setHorizontalHeaderLabels(
            [
                '键',
                '键别名',
                '值',
                '值别名',
                '结果'
            ]
        )
        self.tableMid.verticalHeader().setVisible(False)
        # self.tableMid.horizontalHeader().setSectionResizeMode(
        #     QHeaderView.Stretch)
        self.tableMid.horizontalHeader().setSectionResizeMode(
            QHeaderView.Fixed)
        # self.tableMid.horizontalHeader().setSectionResizeMode(
        #     0, QHeaderView.ResizeToContents)
        self.tableMid.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableMid.setAlternatingRowColors(True)
        self.tableMid.setColumnHidden(4, True)
        self.tableMid.setColumnWidth(0, 110)
        self.tableMid.setColumnWidth(1, 100)
        self.tableMid.setColumnWidth(2, 153)
        self.tableMid.setColumnWidth(3, 100)

        self.tableRight = QTableWidget(0, 3)
        self.tableRight.setFont(self.font)
        self.tableRight.setHorizontalHeaderLabels(
            [
                '键',
                '键别名',
                '值'
            ]
        )
        self.tableRight.verticalHeader().setVisible(False)
        self.tableRight.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.tableRight.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents)
        self.tableRight.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableRight.setAlternatingRowColors(True)

        self.hboxLayoutTableLeft.addWidget(self.tableLeft)
        self.hboxLayoutTableMid.addWidget(self.tableMid)
        self.hboxLayoutTableRight.addWidget(self.tableRight)

        self.groupBoxTableLeft = QGroupBox('验证结果')
        self.groupBoxTableLeft.setLayout(self.hboxLayoutTableLeft)
        self.groupBoxTableMid = QGroupBox('一级数据')
        self.groupBoxTableMid.setLayout(self.hboxLayoutTableMid)
        self.groupBoxTableRight = QGroupBox('二级数据')
        self.groupBoxTableRight.setLayout(self.hboxLayoutTableRight)
        # self.groupBoxTableRight.setVisible(False)
        self.hboxLayoutBody.addWidget(self.groupBoxTableLeft)
        self.hboxLayoutBody.addWidget(self.groupBoxTableMid)
        self.hboxLayoutBody.addWidget(self.groupBoxTableRight)
        self.hboxLayoutBody.setStretchFactor(self.groupBoxTableLeft, 3)
        self.hboxLayoutBody.setStretchFactor(self.groupBoxTableMid, 4)
        self.hboxLayoutBody.setStretchFactor(self.groupBoxTableRight, 2)

        self.mainLayout.addLayout(self.hboxLayoutModeSelectHeader)
        self.mainLayout.addWidget(self.groupBoxSerialHeader)
        self.mainLayout.addLayout(self.hboxLayoutKafkaHeader)
        self.mainLayout.addWidget(self.groupBoxManualHeader)
        self.mainLayout.addLayout(self.hboxLayoutBody)
        self.tabMainUI.setLayout(self.mainLayout)

    def initHintUI(self):
        """
        初始化提示UI
        :return: None
        """
        self.hintLayout = QVBoxLayout()
        self.hintLayout.setContentsMargins(20, 20, 20, 20)

        readme_path = os.path.join(path, 'README.txt')
        self.textEditReadme = QTextEdit()
        self.textEditReadme.setObjectName('textEditReadme')
        self.textEditReadme.setReadOnly(True)
        try:
            with open(readme_path, encoding='utf-8') as f:
                self.textEditReadme.setPlainText(f.read())
        except Exception as e:
            log.error(str(e))

        self.hintLayout.addWidget(self.textEditReadme)
        self.tabHintUI.setLayout(self.hintLayout)

    def loadConfig(self):
        try:
            if config.get('DEFAULT', 'mode') == 'serial':
                self.radioBtnSerialMode.setChecked(True)
            if config.get('DEFAULT', 'mode') == 'kafka':
                self.radioBtnKafkaMode.setChecked(True)
            if config.get('DEFAULT', 'mode') == 'manual':
                self.radioBtnManualMode.setChecked(True)

            dict_['kafka_cur_alias'] = \
                config.get('DEFAULT', 'kafka')
            dict_['kafka_cur_server'] = \
                config.get(dict_['kafka_cur_alias'], 'server')
            dict_['kafka_cur_topic'] = \
                config.get(dict_['kafka_cur_alias'], 'topic')
            dict_['kafka_cur_filter'] = \
                config.get(dict_['kafka_cur_alias'], 'filter')

            self.comboBoxKafkaCluster.addItem(
                re.match(r'kafka_(.+)', dict_['kafka_cur_alias']).group(1))
            self.comboBoxKafkaTopic.addItem(dict_['kafka_cur_topic'])
            self.lineEditSshHost.setText(
                config.get(dict_['kafka_cur_alias'], 'ssh_host'))
            self.lineEditSshPort.setText(
                config.get(dict_['kafka_cur_alias'], 'ssh_port'))
            self.lineEditSshUser.setText(
                config.get(dict_['kafka_cur_alias'], 'ssh_user'))
            self.lineEditSshPwd.setText(
                config.get(dict_['kafka_cur_alias'], 'ssh_pwd'))
            self.groupBoxSshHeader.setEnabled(
                True if config.getboolean(
                    dict_['kafka_cur_alias'], 'ssh_enable') else False)
            self.checkBoxKafkaSshEnable.setCheckState(
                Qt.CheckState(2) if config.getboolean(
                    dict_['kafka_cur_alias'], 'ssh_enable') else Qt.CheckState(0))
            self.lineEditKafkaFilter.setText(
                config.get(dict_['kafka_cur_alias'], 'filter'))

            dict_['serial_cur_cmd'] = config.get('DEFAULT', 'serial')
            dict_['serial_cur_com'] = \
                config.get(dict_['serial_cur_cmd'], 'com')
            dict_['serial_cur_filter'] = \
                config.get(dict_['serial_cur_cmd'], 'filter')

            self.comboBoxSerialCom.addItem(dict_['serial_cur_com'])
            self.comboBoxSerialCmd.addItem(
                re.match(r'serial_(.+)', dict_['serial_cur_cmd']).group(1))
            self.lineEditSerialFilter.setText(
                config.get(dict_['serial_cur_cmd'], 'filter'))
        except Exception as e:
            log.error(str(e))

    def bind(self):
        """
        信号绑定槽函数
        信号绑定槽函数
        :return: None
        """
        self.btnSerialClear.clicked.connect(
            lambda: self.btnSerialClearClicked(self.btnSerialClear))
        self.btnSerialStart.clicked.connect(self.btnSerialStartClicked)
        self.btnSerialStop.clicked.connect(
            lambda: self.btnSerialStopClicked(self.btnSerialStop))
        self.btnSerialTest.clicked.connect(
            lambda: self.btnSerialTestClicked(self.btnSerialTest))
        self.btnKafkaStart.clicked.connect(
            lambda: self.btnKafkaStartClicked(self.btnKafkaStart))
        self.btnKafkaStop.clicked.connect(
            lambda: self.btnKafkaStopClicked(self.btnKafkaStop))
        self.btnKafkaClear.clicked.connect(
            lambda: self.btnSerialClearClicked(self.btnKafkaClear))
        self.btnManualCheck.clicked.connect(
            lambda: self.btnManualCheckClicked(self.btnManualCheck))
        self.btnManualClear.clicked.connect(
            lambda: self.btnManualClearClicked(self.btnManualClear))
        self.comboBoxSerialCom.currentIndexChanged.connect(
            self.comboBoxSerialComSelected)
        self.comboBoxSerialCom.showPopup_.connect(
            self.comboBoxSerialComClicked)
        self.comboBoxSerialCmd.currentIndexChanged.connect(
            self.comboBoxSerialCmdSelected)
        self.comboBoxSerialCmd.showPopup_.connect(
            self.comboBoxSerialCmdClicked)
        self.comboBoxKafkaCluster.showPopup_.connect(
            self.comboBoxKafkaClusterClicked)
        self.comboBoxKafkaCluster.currentIndexChanged.connect(
            self.comboBoxKafkaClusterSelected)
        self.checkBoxKafkaSshEnable.stateChanged.connect(
            lambda: self.checkBoxKafkaSshEnableChanged(
                self.checkBoxKafkaSshEnable))
        self.comboBoxKafkaTopic.showPopup_.connect(
            self.comboBoxKafkaTopicClicked)
        self.comboBoxKafkaTopic.currentIndexChanged.connect(
            self.comboBoxKafkaTopicSelected)
        self.kafkaThread.add.connect(self.checkResultReceived)
        self.kafkaThread.terminal.connect(self.kafkaStopSignalReceived)
        self.lineEditSshHost.textChanged.connect(
            lambda: self.lineEditChanged(self.lineEditSshHost))
        self.lineEditSshPort.textChanged.connect(
            lambda: self.lineEditChanged(self.lineEditSshPort))
        self.lineEditSshUser.textChanged.connect(
            lambda: self.lineEditChanged(self.lineEditSshUser))
        self.lineEditSshPwd.textChanged.connect(
            lambda: self.lineEditChanged(self.lineEditSshPwd))
        self.lineEditKafkaFilter.textChanged.connect(
            lambda: self.lineEditChanged(self.lineEditKafkaFilter))
        self.lineEditSerialFilter.textChanged.connect(
            lambda: self.lineEditChanged(self.lineEditSerialFilter))
        self.radioBtnSerialMode.toggled.connect(
            lambda: self.radioBtnModeToggled(self.radioBtnSerialMode))
        self.radioBtnKafkaMode.toggled.connect(
            lambda: self.radioBtnModeToggled(self.radioBtnKafkaMode))
        self.radioBtnManualMode.toggled.connect(
            lambda: self.radioBtnModeToggled(self.radioBtnManualMode))
        self.tableLeft.cellClicked.connect(self.tableLeftCellClicked)
        self.tableMid.cellClicked.connect(self.tableMidCellClicked)
        self.serialThread.add.connect(self.checkResultReceived)
        self.serialThread.terminal.connect(self.serialStopSignalReceived)

    def btnSerialClearClicked(self, btn):
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
            log.info('Starting!!!')
            if self.kafkaThread.isRunning():
                reply = QMessageBox.information(
                    self, '提示', '该操作将强制结束Kafka通信，请确认！', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.btnKafkaStop.click()
                else:
                    return
            if not dict_['serial_cur_com']:
                log.error("未选择串口端口或Shell命令")
                QMessageBox.information(
                    self, '提示', '请先选择串口端口和Shell命令！', QMessageBox.Ok)
                return

            self.serialThread.working = True
            self.serialThread.start()

            self.row = 0
            self.tableLeft.clearContents()
            self.tableMid.clearContents()
            self.tableRight.clearContents()
            self.comboBoxSerialCom.setEnabled(False)
            self.lineEditSerialFilter.setEnabled(False)
            self.comboBoxSerialCmd.setEnabled(False)
            self.btnSerialStart.setEnabled(False)

            # 添加延时
            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: self.btnSerialStop.setEnabled(True))
            timer.start(5000)

        except Exception as e:
            log.error(str(e))

    def btnSerialStopClicked(self, btn):
        """
        点击结束按钮触发
        :param btn: object
        :return: None
        """
        try:
            self.serialThread.serial.stopReadSerial()
            self.serialThread.serial.close()
            self.serialThread.__del__()
        except Exception as e:
            log.error(str(e))

    def btnSerialTestClicked(self, btn):
            """
            点击自动模式的模拟调试按钮
            :param btn: object
            :return: None
            """
            with open(os.path.join(path, 'conf', 'test.txt')) as f:
                data = f.read()
            test = LogCheck()
            res = test.check_log(data)
            if res:
                self.row = 0
                self.checkResultReceived(res)

    def btnKafkaStartClicked(self, btn):
        """
        点击Kafka开始按钮
        :param btn: object
        :return: None
        """
        try:
            if self.serialThread.isRunning():
                reply = QMessageBox.information(
                    self, '提示', '该操作将强制结束串口通信，请确认！', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.btnSerialStop.click()
                else:
                    return
            if not self.comboBoxKafkaTopic.currentText():
                QMessageBox.information(
                    self, '提示', '请先选择Server和Topic！', QMessageBox.Ok)
                return

            self.kafkaThread.working = True
            self.kafkaThread.start()

            self.row = 0
            self.tableLeft.clearContents()
            self.tableMid.clearContents()
            self.tableRight.clearContents()
            self.groupBoxSshHeader.setEnabled(False)
            self.comboBoxKafkaCluster.setEnabled(False)
            self.lineEditKafkaFilter.setEnabled(False)
            self.comboBoxKafkaTopic.setEnabled(False)
            self.checkBoxKafkaSshEnable.setEnabled(False)
            self.btnKafkaStart.setEnabled(False)

            # 添加延时
            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: self.btnKafkaStop.setEnabled(True))
            timer.start(5000)

        except Exception as e:
            log.error(str(e))

    def btnKafkaStopClicked(self, btn):
        """
        点击Kafka结束按钮
        :param btn: object
        :return: None
        """
        try:
            self.kafkaThread.kafka.stop_kafka()
            self.kafkaThread.__del__()
        except Exception as e:
            log.error(str(e))

    def btnManualCheckClicked(self, btn):
        """
        点击手动模式的验证按钮
        :param btn: object
        :return: None
        """
        try:
            with open(os.path.join(path, 'conf', 'test.txt')) as f:
                data_tmp = f.read()
            data = self.textEditManual.toPlainText() \
                if self.textEditManual.toPlainText().strip() else data_tmp
            log.info('Mock log data: ' + data)
            test = LogCheck()
            res = test.check_log(data)
            if res:
                self.row = 0
                self.checkResultReceived(res)
            log.info('Mock Check result: ' + str(res))
        except Exception as e:
            log.error(str(e))

    def btnManualClearClicked(self, btn):
        """
        点击手动模式的清空按钮
        :param btn: object
        :return: None
        """
        self.textEditManual.clear()
        self.tableLeft.clearContents()
        self.tableMid.clearContents()
        self.tableRight.clearContents()
        self.row = 0

    def checkBoxKafkaSshEnableChanged(self, i):
        """
        SSH启用状态修改
        :param i: object
        :return: None
        """
        if not self.checkBoxKafkaSshEnable.checkState():
            self.groupBoxSshHeader.setEnabled(False)
            config.set(dict_['kafka_cur_alias'], 'ssh_enable', 'false')
        else:
            self.groupBoxSshHeader.setEnabled(True)
            config.set(dict_['kafka_cur_alias'], 'ssh_enable', 'true')

    def checkResultReceived(self, res):
        """
        获得检验结果返回触发
        :param res: dict
        :return: None
        """
        cnt = 0

        if not res:
            return

        try:
            for i in res:
                if not i:
                    continue
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
                    self.tableLeft.setItem(self.row, 3, QTableWidgetItem('正常'))
                    # 绿色表示全部字段均正常
                    self.tableLeft.item(self.row, 3).setBackground(
                        QBrush(QColor(0, 128, 0)))
                    self.setToolTip('所有字段均正常，Ctrl+C可复制内容')
                if i['result'] == 1:
                    self.tableLeft.setItem(self.row, 3, QTableWidgetItem('异常'))
                    # 红色表示部分字段缺失或值错误
                    self.tableLeft.item(self.row, 3).setBackground(
                        QBrush(QColor(255, 0, 0)))
                    self.setToolTip('部分字段缺失或错误，Ctrl+C可复制内容')
                if i['result'] == 2:
                    self.tableLeft.setItem(self.row, 3,
                                           QTableWidgetItem('警告'))
                    # 黄色表示包含未定义字段
                    self.tableLeft.item(self.row, 3).setBackground(
                        QBrush(QColor(255, 255, 0)))
                    self.setToolTip('部分字段不在定义内，Ctrl+C可复制内容')

                self.tableLeft.setItem(self.row, 4, QTableWidgetItem(
                    json.dumps(i['data'])))
                self.tableLeft.setItem(self.row, 5, QTableWidgetItem(
                    json.dumps(i)))

                cnt += 1
                self.row += 1
        except Exception as e:
            log.error(str(e))

    def comboBoxSerialComSelected(self, i):
        """
        下拉框选择端口触发
        :param i: MyComboBox
        :return: None
        """
        try:
            if not self.comboBoxSerialCom.currentText():
                return
            dict_['serial_cur_com'] = re.findall(
                r'COM[0-9]+', self.comboBoxSerialCom.currentText())[0]
            if dict_['serial_cur_cmd']:
                config.set(dict_['serial_cur_cmd'],
                           'com', dict_['serial_cur_com'])
        except Exception as e:
            log.error(str(e))

    def comboBoxSerialComClicked(self):
        """
        点击下拉框
        :return: None
        """
        self.comboBoxSerialCom.clear()
        try:
            portList = getPortList()
            if portList:
                for i in portList:
                    self.comboBoxSerialCom.addItem(i[0])
        except Exception as e:
            log.error(str(e))
            QMessageBox.information(self, '提示', str(e), QMessageBox.Ok)

    def comboBoxSerialCmdSelected(self, i):
        """
        下拉框选择串口命令触发
        :param i: MyComboBox
        :return: None
        """
        try:
            if self.comboBoxSerialCmd.currentText():
                dict_['serial_cur_cmd'] = 'serial_' + self.comboBoxSerialCmd.currentText()
                config.set('DEFAULT', 'serial', dict_['serial_cur_cmd'])
        except Exception as e:
            log.error(str(e))

    def comboBoxSerialCmdClicked(self):
        """
        点击串口命令下拉框
        :return: None
        """
        try:
            self.comboBoxSerialCmd.clear()
            for i in config.sections():
                match = re.match(r'^serial_(.+)', i)
                if match:
                    self.comboBoxSerialCmd.addItem(match.group(1))
        except Exception as e:
            log.error(str(e))
            QMessageBox.information(self, '提示', str(e), QMessageBox.Ok)

    def comboBoxKafkaTopicClicked(self):
        """
        点击kafka topic下拉框
        :return:
        """
        try:
            self.comboBoxKafkaTopic.clear()

            if not config.get(dict_['kafka_cur_alias'], 'group_id'):
                config.set(dict_['kafka_cur_alias'], 'group_id', socket.gethostname())
            kafka_config = {
                'server': dict_['kafka_cur_server'],
                'group_id': config.get(dict_['kafka_cur_alias'], 'group_id')
            }
            ssh_config = {
                'host': config.get(dict_['kafka_cur_alias'], 'ssh_host'),
                'port': config.get(dict_['kafka_cur_alias'], 'ssh_port'),
                'user': config.get(dict_['kafka_cur_alias'], 'ssh_user'),
                'pwd': config.get(dict_['kafka_cur_alias'], 'ssh_pwd')
            } if config.getboolean(dict_['kafka_cur_alias'], 'ssh_enable') else None

            self.kafka = Kafka(kafka_config=kafka_config, ssh_config=ssh_config)
            self.kafka.init_kafka()
            self.kafka_topics = list(self.kafka.topics_kafka())
            log.info(str(self.kafka_topics))
            if self.kafka_topics:
                self.kafka_topics.sort()
                for i in self.kafka_topics:
                    if re.match(r'^json\..+', i):
                        self.comboBoxKafkaTopic.addItem(str(i))
        except Exception as e:
            log.error(str(e))
            QMessageBox.information(self, '提示', '获取Topic失败，请检查配置文件！', QMessageBox.Ok)

    def comboBoxKafkaTopicSelected(self, i):
        """
        选择kafka topic
        :param i: object
        :return: None
        """
        # self.comboBoxKafkaTopic.setCurrentText('test')
        # dict_['kafka_cur_topic'] = 'test'
        dict_['kafka_cur_topic'] = self.comboBoxKafkaTopic.currentText()
        config.set(dict_['kafka_cur_alias'], 'topic', dict_['kafka_cur_topic'])

    def comboBoxKafkaClusterClicked(self):
        """
        点击kafka bootstrap server下拉框
        :return: None
        """
        self.comboBoxKafkaCluster.clear()
        try:
            for i in config.sections():
                match = re.match(r'^kafka_(.+)', i)
                if match:
                    self.comboBoxKafkaCluster.addItem(match.group(1))
        except Exception as e:
            log.error(str(e))

    def comboBoxKafkaClusterSelected(self, i):
        """
        选择kafka bootstrap server
        :param i: object
        :return: None
        """
        try:
            if not self.comboBoxKafkaCluster.currentText():
                return
            dict_['kafka_cur_alias'] = 'kafka_' + self.comboBoxKafkaCluster.currentText()
            dict_['kafka_cur_server'] = config.get(
                dict_['kafka_cur_alias'], 'server')
            config.set('DEFAULT', 'kafka', dict_['kafka_cur_alias'])

            self.lineEditSshHost.setText(
                config.get(dict_['kafka_cur_alias'], 'ssh_host'))
            self.lineEditSshPort.setText(
                config.get(dict_['kafka_cur_alias'], 'ssh_port'))
            self.lineEditSshUser.setText(
                config.get(dict_['kafka_cur_alias'], 'ssh_user'))
            self.lineEditSshPwd.setText(
                config.get(dict_['kafka_cur_alias'], 'ssh_pwd'))
            self.groupBoxSshHeader.setEnabled(
                True if config.getboolean(dict_['kafka_cur_alias'],
                                          'ssh_enable') else False)
            self.checkBoxKafkaSshEnable.setCheckState(
                Qt.CheckState(2) if config.getboolean(dict_['kafka_cur_alias'], 'ssh_enable') else Qt.CheckState(0))
            self.lineEditKafkaFilter.setText(
                config.get(dict_['kafka_cur_alias'], 'filter'))
            self.comboBoxKafkaTopic.clear()
            self.comboBoxKafkaTopic.addItem(config.get(
                dict_['kafka_cur_alias'], 'topic'))
        except Exception as e:
            log.error(str(e))

    def lineEditChanged(self, i):
        """
        修改执行命令触发
        :param i: object
        :return: None
        """
        try:
            if i is self.lineEditSshHost:
                config.set(dict_['kafka_cur_alias'], 'ssh_host', i.text())
            if i is self.lineEditSshPort:
                config.set(dict_['kafka_cur_alias'], 'ssh_port', i.text())
            if i is self.lineEditSshUser:
                config.set(dict_['kafka_cur_alias'], 'ssh_user', i.text())
            if i is self.lineEditSshPwd:
                config.set(dict_['kafka_cur_alias'], 'ssh_pwd', i.text())
            if i is self.lineEditKafkaFilter:
                dict_['kafka_cur_filter'] = i.text()
                config.set(dict_['kafka_cur_alias'], 'filter', i.text())
            if i is self.lineEditSerialFilter:
                dict_['serial_cur_filter'] = i.text()
                config.set(dict_['serial_cur_cmd'], 'filter', i.text())
        except Exception as e:
            log.error(str(e))

    def radioBtnModeToggled(self, i):
        """
        选择手动模式
        :param i: object
        :return: None
        """
        try:
            if i.text() == '串口模式':
                self.groupBoxSerialHeader.setVisible(True)
                self.groupBoxSshHeader.setVisible(False)
                self.groupBoxKafkaHeader.setVisible(False)
                self.groupBoxManualHeader.setVisible(False)
                config.set('DEFAULT', 'mode', 'serial')

            if i.text() == 'Kafka模式':
                self.groupBoxSerialHeader.setVisible(False)
                self.groupBoxSshHeader.setVisible(True)
                self.groupBoxKafkaHeader.setVisible(True)
                self.groupBoxManualHeader.setVisible(False)
                config.set('DEFAULT', 'mode', 'kafka')

            if i.text() == '手动模式':
                self.groupBoxSerialHeader.setVisible(False)
                self.groupBoxSshHeader.setVisible(False)
                self.groupBoxKafkaHeader.setVisible(False)
                self.groupBoxManualHeader.setVisible(True)
                config.set('DEFAULT', 'mode', 'manual')
        except Exception as e:
            log.error(str(e))

    def serialStopSignalReceived(self, text):
        """
        Serial子线程结束触发提示
        :param text: str
        :return:
        """
        try:
            self.comboBoxSerialCom.setEnabled(True)
            self.lineEditSerialFilter.setEnabled(True)
            self.comboBoxSerialCmd.setEnabled(True)
            self.btnSerialStart.setEnabled(True)
            self.btnSerialStop.setEnabled(False)
            QMessageBox.information(self, '提示', text, QMessageBox.Ok)
        except Exception as e:
            log.error(str(e))

    def kafkaStopSignalReceived(self, text):
        """
        Kafka子线程结束触发提示
        :param text: str
        :return:
        """
        try:
            self.groupBoxSshHeader.setEnabled(True)
            self.comboBoxKafkaCluster.setEnabled(True)
            self.lineEditKafkaFilter.setEnabled(True)
            self.comboBoxKafkaTopic.setEnabled(True)
            self.checkBoxKafkaSshEnable.setEnabled(True)
            self.btnKafkaStart.setEnabled(True)
            self.btnKafkaStop.setEnabled(False)
            QMessageBox.information(self, '提示', text, QMessageBox.Ok)
        except Exception as e:
            log.error(str(e))

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
                self.tableMid.setRowCount(len(dictRes['data']) + len(dictRes['missing_key']))
                for k in dictRes['data']:
                    self.tableMid.setItem(n, 0, QTableWidgetItem(str(k)))
                    self.tableMid.setItem(n, 1, QTableWidgetItem(str(dictRes['data'][k].get('key_alias')) if dictRes['data'][k].get('key_alias') else 'N/A'))
                    self.tableMid.setItem(n, 2, QTableWidgetItem(str(dictRes['data'][k].get('value'))))
                    self.tableMid.setItem(n, 3, QTableWidgetItem(
                        str(dictRes['data'][k].get('value'))))

                    if k in dictRes['invalid_key']:
                        self.tableMid.setItem(n, 4, QTableWidgetItem('不符合'))
                        for i in range(self.tableMid.columnCount()):
                            self.tableMid.item(n, i).setBackground(QBrush(QColor(255, 0, 0)))
                            self.tableMid.item(n, i).setFont()

                    elif k in dictRes['undefined_key']:
                        self.tableMid.setItem(n, 4, QTableWidgetItem('未定义'))
                        for i in range(self.tableMid.columnCount()):
                            self.tableMid.item(n, i).setBackground(QBrush(QColor(255, 255, 0)))
                    else:
                        self.tableMid.setItem(n, 4, QTableWidgetItem('符合'))
                    n += 1

                for i in dictRes['missing_key']:
                    self.tableMid.setItem(n, 0, QTableWidgetItem(str(i)))
                    self.tableMid.setItem(n, 1, QTableWidgetItem(str(dictRes['missing_key'][i].get('key_alias'))))
                    self.tableMid.setItem(n, 2, QTableWidgetItem('N/A'))
                    self.tableMid.setItem(n, 3, QTableWidgetItem('N/A'))
                    self.tableMid.setItem(n, 4, QTableWidgetItem('未上报'))
                    for k in range(self.tableMid.columnCount()):
                        self.tableMid.item(n, k).setBackground(
                            QBrush(QColor(255, 0, 0)))
                    n += 1
                self.tableMid.setSortingEnabled(True)
                self.tableMid.sortByColumn(0, Qt.AscendingOrder)
        except Exception as e:
            log.error(str(e))

    def tableMidCellClicked(self, row):
        """
        点击tableMid每行数据触发，如果是JSON则解析在tableRight展示
        :param row: int
        :return: None
        """
        try:
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
        except Exception as e:
            log.error(str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = LogCheckUI()
    qss_path = os.path.join(path, 'style.qss')
    with open(qss_path, 'r') as f_:
        qssStyle = f_.read()
    main.setStyleSheet(qssStyle)
    main.show()
    sys.exit(app.exec_())
