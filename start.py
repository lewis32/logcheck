import sys
import json
import os
import re
from configparser import *
from socket import gethostname
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from myUI import Ui_TabWidget
from core.log_check import LogCheck
from core.package.myserial import MySerial as Serial
from core.package.mykafka import MyKafka as Kafka
from core.package.mylogging import MyLogging as Logging
from core.package.mycombobox import MyComboBox as QComboBox

path = os.path.abspath((os.path.dirname(os.path.realpath(__file__))))
log = Logging.getLogger("start")

dict_ = {
    "kafka_cur_alias": "",
    "kafka_cur_server": "",
    "kafka_cur_topic": "",
    "kafka_cur_filter": "",
    "cur_row": 0,
    "serial_cur_port": "",
    "serial_cur_cmd": "",
    "serial_cur_filter": ""
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
            self.serial = Serial(dict_["serial_cur_port"])
            self.serial.send_command(
                config.get(dict_["serial_cur_cmd"], "start_cmd"))

            # self.serial.serial.flushOutput()
            # self.serial.serial.flushInput()

            self.lc = LogCheck()
            while self.working:
                block = self.serial.serial.read(size=10000).decode(
                        "utf-8", errors="ignore")
                if block.strip():
                    log.info("Original log data: " + block)
                    res = self.lc.check_log(block, dict_["serial_cur_filter"].strip())
                    if res:
                        log.info("Check result: " + str(res))
                        self.add.emit(res)
                self.sleep(1)
            self.terminal.emit("串口通信正常结束！")
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
                "server": dict_["kafka_cur_server"],
                "group_id": config.get(dict_["kafka_cur_alias"], "group_id")
            }
            ssh_config = {
                "host": config.get(dict_["kafka_cur_alias"], "ssh_host"),
                "port": config.get(dict_["kafka_cur_alias"], "ssh_port"),
                "user": config.get(dict_["kafka_cur_alias"], "ssh_user"),
                "pwd": config.get(dict_["kafka_cur_alias"], "ssh_pwd")
            } if config.getboolean(
                dict_["kafka_cur_alias"], "ssh_enable") else None

            self.kafka = Kafka(kafka_config=kafka_server, ssh_config=ssh_config)
            self.kafka.init_kafka()
            self.kafka.subscribe_kafka(topics=[dict_["kafka_cur_topic"]])
            self.lc = LogCheck()
            log.info(self.currentThreadId())
            while self.working:
                block = self.kafka.poll_kafka()
                if block and block.strip():
                    log.info("Log data: " + block)
                    res = self.lc.check_log(block, dict_["kafka_cur_filter"].strip())
                    if res:
                        log.info("Log check result: " + str(res))
                        self.add.emit(res)
                self.sleep(1)
            self.terminal.emit("Kafka通信正常结束！")
        except Exception as e:

            log.error(str(e))
            self.terminal.emit(str(e))


class MyUI(QTabWidget, Ui_TabWidget):
    def __init__(self):
        super(MyUI, self).__init__()
        self.setupUi(self)
        self.serialThread = SerialThread()
        self.kafkaThread = KafkaThread()
        self.bind()
        self.loadConfig()

    def closeEvent(self, event):
        try:
            with open(os.path.join(path, "conf", "cfg.ini"), "w") as f:
                config.write(f)
            event.accept()
        except Exception as e:
            log.error(str(e))

    def loadConfig(self):
        try:
            global config
            config = ConfigParser()
            config.read(os.path.join(path, "conf", "cfg.ini"))

            if config.get("DEFAULT", "mode") == "serial":
                self.rBtnSerial.setChecked(True)
            if config.get("DEFAULT", "mode") == "kafka":
                self.rBtnKafka.setChecked(True)
            if config.get("DEFAULT", "mode") == "manual":
                self.rBtnManual.setChecked(True)

            dict_["kafka_cur_alias"] = \
                config.get("DEFAULT", "kafka")
            dict_["kafka_cur_server"] = \
                config.get(dict_["kafka_cur_alias"], "server")
            dict_["kafka_cur_topic"] = \
                config.get(dict_["kafka_cur_alias"], "topic")
            dict_["kafka_cur_filter"] = \
                config.get(dict_["kafka_cur_alias"], "filter")

            self.cBoxKafkaServer.addItem(
                re.match(r"kafka_(.+)", dict_["kafka_cur_alias"]).group(1))
            self.cBoxKafkaTopic.addItem(dict_["kafka_cur_topic"])
            # self.lineEditSshHost.setText(
            #     config.get(dict_["kafka_cur_alias"], "ssh_host"))
            # self.lineEditSshPort.setText(
            #     config.get(dict_["kafka_cur_alias"], "ssh_port"))
            # self.lineEditSshUser.setText(
            #     config.get(dict_["kafka_cur_alias"], "ssh_user"))
            # self.lineEditSshPwd.setText(
            #     config.get(dict_["kafka_cur_alias"], "ssh_pwd"))
            # self.groupBoxSshHeader.setEnabled(
            #     True if config.getboolean(
            #         dict_["kafka_cur_alias"], "ssh_enable") else False)
            # self.cBoxKafkaSshEnable.setCheckState(
            #     Qt.CheckState(2) if config.getboolean(
            #         dict_["kafka_cur_alias"], "ssh_enable") else Qt.CheckState(0))
            self.editKafkaFilter.setText(
                config.get(dict_["kafka_cur_alias"], "filter"))

            dict_["serial_cur_cmd"] = config.get("DEFAULT", "serial")
            dict_["serial_cur_port"] = \
                config.get(dict_["serial_cur_cmd"], "port")
            dict_["serial_cur_filter"] = \
                config.get(dict_["serial_cur_cmd"], "filter")

            self.cBoxSerialPort.addItem(dict_["serial_cur_port"])
            self.cBoxSerialCmd.addItem(
                re.match(r"serial_(.+)", dict_["serial_cur_cmd"]).group(1))
            self.editSerialFilter.setText(
                config.get(dict_["serial_cur_cmd"], "filter"))
            self.tableResList.setColumnHidden(4, True)
            self.tableResList.setColumnHidden(5, True)
        except Exception as e:
            log.error(str(e))

    def bind(self):
        """
        信号绑定槽函数
        :return: None
        """
        self.btnSerialClear.clicked.connect(
            lambda: self.btnClearClicked(self.btnSerialClear))
        self.btnSerialStart.clicked.connect(self.btnSerialStartClicked)
        self.btnSerialStop.clicked.connect(
            lambda: self.btnSerialStopClicked(self.btnSerialStop))
        self.btnKafkaClear.clicked.connect(
            lambda: self.btnClearClicked(self.btnKafkaClear))
        self.btnKafkaEdit.clicked.connect(
            lambda: self.btnKafkaEditClicked(self.btnKafkaEdit))
        self.btnKafkaStart.clicked.connect(
            lambda: self.btnKafkaStartClicked(self.btnKafkaStart))
        self.btnKafkaStop.clicked.connect(
            lambda: self.btnKafkaStopClicked(self.btnKafkaStop))
        self.btnManualStart.clicked.connect(
            lambda: self.btnManualCheckClicked(self.btnManualStart))
        self.btnManualClear.clicked.connect(
            lambda: self.btnClearClicked(self.btnManualClear))
        self.cBoxSerialPort.currentIndexChanged.connect(
            self.cBoxSerialPortSelected)
        # self.cBoxSerialPort.showPopup_.connect(
        #     self.cBoxSerialPortClicked)
        self.cBoxSerialCmd.currentIndexChanged.connect(
            self.cBoxSerialCmdSelected)
        # self.cBoxSerialCmd.showPopup_.connect(
        #     self.cBoxSerialCmdClicked)
        # self.cBoxKafkaCluster.showPopup_.connect(
        #     self.cBoxKafkaClusterClicked)
        self.cBoxKafkaServer.currentIndexChanged.connect(
            self.cBoxKafkaServerSelected)
        # self.checkBoxKafkaSshEnable.stateChanged.connect(
        #     lambda: self.checkBoxKafkaSshEnableChanged(
        #         self.checkBoxKafkaSshEnable))
        # self.cBoxKafkaTopic.showPopup_.connect(
        #     self.cBoxKafkaTopicClicked)
        self.cBoxKafkaTopic.currentIndexChanged.connect(
            self.cBoxKafkaTopicSelected)
        self.kafkaThread.add.connect(self.checkResultReceived)
        self.kafkaThread.terminal.connect(self.kafkaStopSignalReceived)
        # self.editSshHost.textChanged.connect(
        #     lambda: self.lineEditChanged(self.lineEditSshHost))
        # self.editSshPort.textChanged.connect(
        #     lambda: self.lineEditChanged(self.lineEditSshPort))
        # self.editSshUser.textChanged.connect(
        #     lambda: self.lineEditChanged(self.lineEditSshUser))
        # self.editSshPwd.textChanged.connect(
        #     lambda: self.lineEditChanged(self.lineEditSshPwd))
        self.editKafkaFilter.textChanged.connect(
            lambda: self.editChanged(self.editKafkaFilter))
        self.editSerialFilter.textChanged.connect(
            lambda: self.editChanged(self.editSerialFilter))
        self.rBtnSerial.toggled.connect(
            lambda: self.rBtnToggled(self.rBtnSerial))
        self.rBtnKafka.toggled.connect(
            lambda: self.rBtnToggled(self.rBtnKafka))
        self.rBtnManual.toggled.connect(
            lambda: self.rBtnToggled(self.rBtnManual))
        self.tableResList.cellClicked.connect(self.tableResListCellClicked)
        self.tableRes.cellClicked.connect(self.tableResCellClicked)
        self.serialThread.add.connect(self.checkResultReceived)
        self.serialThread.terminal.connect(self.serialStopSignalReceived)

    def btnClearClicked(self, btn):
        """
        点击清空按钮触发
        :param btn: object
        :return: None
        """
        if btn is self.btnManualClear:
            self.editManual.clear()
        self.tableResList.clearContents()
        self.tableResList.setRowCount(0)
        self.tableRes.clearContents()
        self.tableRes.setRowCount(0)
        # self.tableR.clearContents()
        # self.tableR.setRowCount(0)
        dict_["cur_row"] = 0

    def btnSerialStartClicked(self, btn):
        """
        点击开始按钮触发
        :param btn: object
        :return: None
        """
        if self.kafkaThread.isRunning():
            reply = QMessageBox.information(
                self, "提示", "该操作将强制结束Kafka通信，请确认！",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.btnKafkaStop.click()
            else:
                return
        if not dict_["serial_cur_port"]:
            log.error("未选择串口端口或Shell命令")
            QMessageBox.information(
                self, "提示", "请先选择串口端口和Shell命令！", QMessageBox.Ok)
            return

        self.serialThread.working = True
        self.serialThread.start()

        dict_["cur_row"] = 0
        self.tableResList.clearContents()
        self.tableResList.setRowCount(0)
        self.tableRes.clearContents()
        self.tableRes.setRowCount(0)
        # self.tableR.clearContents()
        # self.tableR.setRowCount(0)
        self.cBoxSerialPort.setEnabled(False)
        self.editSerialFilter.setEnabled(False)
        self.cBoxSerialCmd.setEnabled(False)
        self.btnSerialStart.setEnabled(False)

        # 添加延时
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: self.btnSerialStop.setEnabled(True))
        timer.start(5000)

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

    def btnKafkaEditClicked(self, btn):
        """
        点击Kafka编辑按钮
        :param btn: object
        :return: None
        """
        dialog = QDialog()
        btn = QPushButton("test", dialog)
        dialog.setWindowTitle("test")
        dialog.setFixedSize(500, 500)
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.exec_()

    def btnKafkaStartClicked(self, btn):
        """
        点击Kafka开始按钮
        :param btn: object
        :return: None
        """
        if self.serialThread.isRunning():
            reply = QMessageBox.information(
                self, "提示", "该操作将强制结束串口通信，请确认！",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.btnSerialStop.click()
            else:
                return
        if not self.cBoxKafkaTopic.currentText():
            QMessageBox.information(
                self, "提示", "请先选择Server和Topic！", QMessageBox.Ok)
            return

        self.kafkaThread.working = True
        self.kafkaThread.start()
        dict_["cur_row"] = 0
        self.tableResList.clearContents()
        self.tableRes.clearContents()
        # self.tableR.clearContents()
        self.tableResList.setRowCount(0)
        self.tableRes.setRowCount(0)
        # self.tableR.setRowCount(0)
        self.btnKafkaStart.setEnabled(False)
        # self.checkBoxKafkaSshEnable.setEnabled(False)
        self.cBoxKafkaServer.setEnabled(False)
        self.cBoxKafkaTopic.setEnabled(False)
        # self.groupBoxSshHeader.setEnabled(False)
        self.editKafkaFilter.setEnabled(False)
        # 添加延时
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: self.btnKafkaStop.setEnabled(True))
        timer.start(5000)

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
            with open(os.path.join(path, "conf", "test.txt")) as f:
                data_tmp = f.read()
            data = self.editManual.toPlainText() \
                if self.editManual.toPlainText().strip() else data_tmp
            log.info("Mock log data: " + data)
            test = LogCheck()
            res = test.check_log(data)
            if res:
                dict_["cur_row"] = 0
                self.checkResultReceived(res)
            log.info("Mock Check result: " + str(res))
        except Exception as e:
            log.error(str(e))

    def cBoxKafkaSshEnableChanged(self, i):
        """
        SSH启用状态修改
        :param i: object
        :return: None
        """
        if not self.checkBoxKafkaSshEnable.checkState():
            self.groupBoxSshHeader.setEnabled(False)
            config.set(dict_["kafka_cur_alias"], "ssh_enable", "false")
        else:
            self.groupBoxSshHeader.setEnabled(True)
            config.set(dict_["kafka_cur_alias"], "ssh_enable", "true")

    def checkResultReceived(self, res):
        """
        获得检验结果返回触发
        :param res: dict
        :return: None
        """
        row = dict_["cur_row"]

        if not res:
            return

        for i in res:
            self.tableResList.setRowCount(row + 1)
            self.tableResList.setItem(row, 0, QTableWidgetItem(
                str(i["src_event_code"]) if i["src_event_code"] else "N/A"))
            self.tableResList.setItem(row, 1, QTableWidgetItem(
                str(i["event_code"]) if i["event_code"] else "N/A"))
            self.tableResList.setItem(row, 2, QTableWidgetItem(
                str(i["event_alias"]) if i["event_alias"] else "N/A"))
            self.tableResList.item(row, 2).setToolTip(
                str(i["event_alias"]) if i["event_alias"] else "N/A")

            if i["result"] == -1:
                self.tableResList.setItem(row, 3, QTableWidgetItem(
                    QIcon("./assets/question_mark.png"), ""))
            if i["result"] == 0:
                self.tableResList.setItem(row, 3, QTableWidgetItem(
                    QIcon("./assets/check_mark.png"), ""))
            if i["result"] == 1:
                self.tableResList.setItem(row, 3, QTableWidgetItem(
                    QIcon("./assets/cross_mark.png"), ""))
            if i["result"] == 2:
                self.tableResList.setItem(row, 3, QTableWidgetItem(
                    QIcon("./assets/exclamation_mark.png"), ""))
            self.tableResList.setItem(row, 4, QTableWidgetItem(
                json.dumps(i["data"])))
            self.tableResList.setItem(row, 5, QTableWidgetItem(
                json.dumps(i)))
            row += 1
        dict_["cur_row"] = row

    def cBoxSerialPortSelected(self, i):
        """
        下拉框选择端口触发
        :param i: QComboBox
        :return: None
        """
        try:
            if not self.cBoxSerialPort.currentText():
                return
            dict_["serial_cur_port"] = re.findall(
                r"COM[0-9]+", self.cBoxSerialPort.currentText())[0]
            if dict_["serial_cur_cmd"]:
                config.set(dict_["serial_cur_cmd"],
                           "port", dict_["serial_cur_port"])
        except Exception as e:
            log.error(str(e))

    def cBoxSerialPortClicked(self):
        """
        点击下拉框
        :return: None
        """
        self.cBoxSerialPort.clear()
        try:
            portList = Serial.get_port_list()
            if portList:
                for i in portList:
                    self.cBoxSerialPort.addItem(i[0])
        except Exception as e:
            log.error(str(e))
            QMessageBox.information(self, "提示", str(e), QMessageBox.Ok)

    def cBoxSerialCmdSelected(self, i):
        """
        下拉框选择串口命令触发
        :param i: QComboBox
        :return: None
        """
        try:
            if self.cBoxSerialCmd.currentText():
                dict_["serial_cur_cmd"] = "serial_" + self.cBoxSerialCmd.currentText()
                config.set("DEFAULT", "serial", dict_["serial_cur_cmd"])
        except Exception as e:
            log.error(str(e))

    def cBoxSerialCmdClicked(self):
        """
        点击串口命令下拉框
        :return: None
        """
        try:
            self.cBoxSerialCmd.clear()
            for i in config.sections():
                match = re.match(r"^serial_(.+)", i)
                if match:
                    self.cBoxSerialCmd.addItem(match.group(1))
        except Exception as e:
            log.error(str(e))
            QMessageBox.information(self, "提示", str(e), QMessageBox.Ok)

    def cBoxKafkaTopicClicked(self):
        """
        点击kafka topic下拉框
        :return:
        """
        try:
            self.cBoxKafkaTopic.clear()

            if not config.get(dict_["kafka_cur_alias"], "group_id"):
                config.set(dict_["kafka_cur_alias"], "group_id", gethostname())
            kafka_config = {
                "server": dict_["kafka_cur_server"],
                "group_id": config.get(dict_["kafka_cur_alias"], "group_id")
            }
            ssh_config = {
                "host": config.get(dict_["kafka_cur_alias"], "ssh_host"),
                "port": config.get(dict_["kafka_cur_alias"], "ssh_port"),
                "user": config.get(dict_["kafka_cur_alias"], "ssh_user"),
                "pwd": config.get(dict_["kafka_cur_alias"], "ssh_pwd")
            } if config.getboolean(dict_["kafka_cur_alias"], "ssh_enable") else None

            self.kafka = Kafka(kafka_config=kafka_config, ssh_config=ssh_config)
            self.kafka.init_kafka()
            self.kafka_topics = list(self.kafka.topics_kafka())
            log.info(str(self.kafka_topics))
            if self.kafka_topics:
                self.kafka_topics.sort()
                for i in self.kafka_topics:
                    if re.match(r"^json\..+", i):
                        self.cBoxKafkaTopic.addItem(str(i))
            self.kafka.stop_kafka()
        except Exception as e:
            log.error(str(e))
            QMessageBox.information(self, "提示", "获取Topic失败，请检查配置文件！", QMessageBox.Ok)

    def cBoxKafkaTopicSelected(self, i):
        """
        选择kafka topic
        :param i: object
        :return: None
        """
        # self.comboBoxKafkaTopic.setCurrentText("test")
        # dict_["kafka_cur_topic"] = "test"
        dict_["kafka_cur_topic"] = self.cBoxKafkaTopic.currentText()
        config.set(dict_["kafka_cur_alias"], "topic", dict_["kafka_cur_topic"])

    def cBoxKafkaServerClicked(self):
        """
        点击kafka bootstrap server下拉框
        :return: None
        """
        self.cKafkaServer.clear()
        try:
            for i in config.sections():
                match = re.match(r"^kafka_(.+)", i)
                if match:
                    self.cBoxKafkaServer.addItem(match.group(1))
        except Exception as e:
            log.error(str(e))

    def cBoxKafkaServerSelected(self, i):
        """
        选择kafka bootstrap server
        :param i: object
        :return: None
        """
        try:
            if not self.cBoxKafkaServer.currentText():
                return
            dict_["kafka_cur_alias"] = "kafka_" + self.cBoxKafkaServer.currentText()
            dict_["kafka_cur_server"] = config.get(
                dict_["kafka_cur_alias"], "server")
            config.set("DEFAULT", "kafka", dict_["kafka_cur_alias"])

            # self.lineEditSshHost.setText(
            #     config.get(dict_["kafka_cur_alias"], "ssh_host"))
            # self.lineEditSshPort.setText(
            #     config.get(dict_["kafka_cur_alias"], "ssh_port"))
            # self.lineEditSshUser.setText(
            #     config.get(dict_["kafka_cur_alias"], "ssh_user"))
            # self.lineEditSshPwd.setText(
            #     config.get(dict_["kafka_cur_alias"], "ssh_pwd"))
            # self.groupBoxSshHeader.setEnabled(
            #     True if config.getboolean(dict_["kafka_cur_alias"],
            #                               "ssh_enable") else False)
            # self.checkBoxKafkaSshEnable.setCheckState(
            #     Qt.CheckState(2) if config.getboolean(dict_["kafka_cur_alias"], "ssh_enable") else Qt.CheckState(0))
            self.editKafkaFilter.setText(
                config.get(dict_["kafka_cur_alias"], "filter"))
            self.cBoxKafkaTopic.clear()
            self.cBoxKafkaTopic.addItem(config.get(
                dict_["kafka_cur_alias"], "topic"))
        except Exception as e:
            log.error(str(e))

    def editChanged(self, i):
        """
        修改执行命令触发
        :param i: object
        :return: None
        """
        try:
            # if i is self.lineEditSshHost:
            #     config.set(dict_["kafka_cur_alias"], "ssh_host", i.text())
            # if i is self.lineEditSshPort:
            #     config.set(dict_["kafka_cur_alias"], "ssh_port", i.text())
            # if i is self.lineEditSshUser:
            #     config.set(dict_["kafka_cur_alias"], "ssh_user", i.text())
            # if i is self.lineEditSshPwd:
            #     config.set(dict_["kafka_cur_alias"], "ssh_pwd", i.text())
            if i is self.editKafkaFilter:
                dict_["kafka_cur_filter"] = i.text()
                config.set(dict_["kafka_cur_alias"], "filter", i.text())
            if i is self.editSerialFilter:
                dict_["serial_cur_filter"] = i.text()
                config.set(dict_["serial_cur_cmd"], "filter", i.text())
        except Exception as e:
            log.error(str(e))

    def rBtnToggled(self, i):
        """
        选择手动模式
        :param i: object
        :return: None
        """
        try:
            if i.text() == "串口模式":
                self.gBoxSerial.setVisible(True)
                # self.groupBoxSshHeader.setVisible(False)
                self.gBoxKafka.setVisible(False)
                self.gBoxManual.setVisible(False)
                config.set("DEFAULT", "mode", "serial")

            if i.text() == "Kafka模式":
                self.gBoxSerial.setVisible(False)
                # self.groupBoxSshHeader.setVisible(False)
                self.gBoxKafka.setVisible(True)
                self.gBoxManual.setVisible(False)
                config.set("DEFAULT", "mode", "kafka")

            if i.text() == "手动模式":
                self.gBoxSerial.setVisible(False)
                # self.groupBoxSshHeader.setVisible(False)
                self.gBoxKafka.setVisible(False)
                self.gBoxManual.setVisible(True)
                config.set("DEFAULT", "mode", "manual")
        except Exception as e:
            log.error(str(e))

    def serialStopSignalReceived(self, text):
        """
        Serial子线程结束触发提示
        :param text: str
        :return:
        """
        try:
            self.cBoxSerialPort.setEnabled(True)
            self.editSerialFilter.setEnabled(True)
            self.cBoxSerialCmd.setEnabled(True)
            self.btnSerialStart.setEnabled(True)
            self.btnSerialStop.setEnabled(False)
            QMessageBox.information(self, "提示", text, QMessageBox.Ok)
        except Exception as e:
            log.error(str(e))

    def kafkaStopSignalReceived(self, text):
        """
        Kafka子线程结束触发提示
        :param text: str
        :return:
        """
        try:
            # self.gBoxSshHeader.setEnabled(True)
            self.cBoxKafkaServer.setEnabled(True)
            self.editKafkaFilter.setEnabled(True)
            self.cBoxKafkaTopic.setEnabled(True)
            # self.cBoxKafkaSshEnable.setEnabled(True)
            self.btnKafkaStart.setEnabled(True)
            self.btnKafkaStop.setEnabled(False)
            QMessageBox.information(self, "提示", text, QMessageBox.Ok)
        except Exception as e:
            log.error(str(e))

    def tableResListCellClicked(self, row):
        """
        点击基本结果每行数据触发
        :param row: int
        :return: None
        """
        try:
            self.tableRes.clearContents()
            self.tableRes.setRowCount(0)
            # self.tableR.clearContents()
            # self.tableR.setRowCount(0)

            if self.tableResList.item(row, 4) and self.tableResList.item(row, 5):
                self.tableRes.setSortingEnabled(False)
                dictData = json.loads(self.tableResList.item(row, 4).text())
                dictRes = json.loads(self.tableResList.item(row, 5).text())
                n = 0
                self.tableRes.setRowCount(len(dictRes["data"]) + len(dictRes["missing_key"]))
                for key in dictRes["data"]:
                    key_alias = dictRes["data"][key].get("key_alias")
                    value = dictRes["data"][key].get("value")
                    value_alias = dictRes["data"][key].get("value_alias")

                    self.tableRes.setItem(n, 0, QTableWidgetItem(str(key)))
                    self.tableRes.item(n, 0).setToolTip(str(key))
                    self.tableRes.setItem(n, 1, QTableWidgetItem(
                        str(key_alias) if key_alias else "N/A"))
                    self.tableRes.item(n, 1).setToolTip(
                        str(key_alias) if key_alias else "N/A")
                    self.tableRes.setItem(n, 2, QTableWidgetItem(
                        str(value) if value else "N/A"))
                    self.tableRes.item(n, 2).setToolTip(
                        str(value) if value else "N/A")
                    self.tableRes.setItem(n, 3, QTableWidgetItem(
                        str(value_alias) if value_alias else "N/A"))
                    self.tableRes.item(n, 3).setToolTip(
                        str(value_alias) if value_alias else "N/A")
                    if key in dictRes["invalid_key"]:
                        for i in range(self.tableRes.columnCount()):
                            self.tableRes.item(n, i).setBackground(QBrush(QColor(255, 99, 71)))

                    if key in dictRes["undefined_key"]:
                        for i in range(self.tableRes.columnCount()):
                            self.tableRes.item(n, i).setBackground(QBrush(QColor(0, 206, 209)))
                    n += 1

                for i in dictRes["missing_key"]:
                    self.tableRes.setItem(n, 0, QTableWidgetItem(str(i)))
                    self.tableRes.setItem(n, 1, QTableWidgetItem(str(dictRes["missing_key"][i].get("key_alias"))))
                    self.tableRes.setItem(n, 2, QTableWidgetItem("N/A"))
                    self.tableRes.setItem(n, 3, QTableWidgetItem("N/A"))
                    for k in range(self.tableRes.columnCount()):
                        self.tableRes.item(n, k).setBackground(
                            QBrush(QColor(255, 215, 0)))
                    n += 1
                self.tableRes.setSortingEnabled(True)
                self.tableRes.sortByColumn(0, Qt.AscendingOrder)
        except Exception as e:
            log.error(str(e))

    def tableResCellClicked(self, row):
        """
        点击tableMid每行数据触发，如果是JSON则解析在tableRight展示
        :param row: int
        :return: None
        """
        try:
            dialog = QDialog()
            table = QTableWidget(0, 4, dialog)
            table.setFont(self.font)
            table.setHorizontalHeaderLabels(["键", "别名", "值", "别名"])
            table.verticalHeader().setVisible(False)
            table.horizontalHeader().setSectionResizeMode(
                QHeaderView.Fixed)
            table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            table.setAlternatingRowColors(True)
            table.setColumnWidth(0, 100)
            table.setColumnWidth(1, 90)
            table.setColumnWidth(2, 100)
            table.setColumnWidth(3, 90)
            table.clearContents()
            table.setRowCount(0)
            text = self.tableRes.item(row, 2).text()
            if not re.match(r"^{.*}$", text):
                return
            data = json.loads(text)
            # self.tableR.setRowCount(len(data))
            n = 0
            for k in data:
                key_alias = data[k].get("key_alias")
                value = data[k].get("value")
                value_alias = data[k].get("value_alias")
                table.setItem(n, 0, QTableWidgetItem(str(k)))
                table.item(n, 0).setToolTip(str(k))
                table.setItem(n, 1, QTableWidgetItem(str(key_alias) if key_alias else "N/A"))
                table.item(n, 1).setToolTip(str(key_alias) if key_alias else "N/A")
                table.setItem(n, 2, QTableWidgetItem(str(value) if value else "N/A"))
                table.item(n, 2).setToolTip(str(value) if value else "N/A")
                table.setItem(n, 3, QTableWidgetItem(str(value_alias) if value_alias else "N/A"))
                table.item(n, 3).setToolTip(str(value_alias) if value_alias else "N/A")
                n += 1
            dialog.exec_()
        except Exception as e:
            log.error(str(e))
            print(e)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MyUI()
    main.show()
    sys.exit(app.exec_())
