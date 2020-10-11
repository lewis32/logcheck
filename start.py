import sys
import json
import os
import re
import subprocess
from configparser import ConfigParser
from socket import gethostname
from PyQt5.QtWidgets import (QApplication,
                             QDialog,
                             QMainWindow,
                             QMessageBox,
                             QTableWidgetItem)
from PyQt5.QtCore import pyqtSignal, Qt, QTimer, QThread
from PyQt5.QtGui import QBrush, QColor, QIcon
from myUI import Ui_MainWindow
from dialogMore import Ui_Dialog
from core.log_check import LogCheck
from core.package.myserial import MySerial as Serial
from core.package.mykafka import MyKafka as Kafka
from core.package.mylogging import MyLogging as Logging
# from core.package.mycombobox import MyComboBox as QComboBox

path = os.path.abspath((os.path.dirname(os.path.realpath(__file__))))
log = Logging.getLogger("start")

dict_ = {
    "cur_row": 0,
    "kafka_cur_alias": "",
    "kafka_cur_dec": False,
    "kafka_cur_filter": "",
    "kafka_cur_server": "",
    "kafka_cur_topic": "",
    "serial_cur_cmd": "",
    "serial_cur_dec": False,
    "serial_cur_filter": "",
    "serial_cur_port": ""
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
                self.config.get(dict_["serial_cur_cmd"], "start_cmd"))

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
                "group_id": self.config.get(dict_["kafka_cur_alias"], "group_id")
            }
            ssh_config = {
                "host": self.config.get(dict_["kafka_cur_alias"], "ssh_host"),
                "port": self.config.get(dict_["kafka_cur_alias"], "ssh_port"),
                "user": self.config.get(dict_["kafka_cur_alias"], "ssh_user"),
                "pwd": self.config.get(dict_["kafka_cur_alias"], "ssh_pwd")
            } if self.config.getboolean(
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


class MyUI(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MyUI, self).__init__()
        self.setupUi(self)
        self.serialThread = SerialThread()
        self.kafkaThread = KafkaThread()
        self.bind()
        self.loadConfig()

    def closeEvent(self, event):
        try:
            if self.tabWidget.currentWidget() == self.tabSerial:
                self.config.set("DEFAULT", "mode", "serial")
            if self.tabWidget.currentWidget() == self.tabKafka:
                self.config.set("DEFAULT", "mode", "kafka")
            if self.tabWidget.currentWidget() == self.tabManual:
                self.config.set("DEFAULT", "mode", "manual")
            with open(os.path.join(path, "conf", "cfg.ini"), "w") as f:
                self.config.write(f)
            event.accept()
        except Exception as e:
            log.error(str(e))

    def loadConfig(self):
        try:
            self.config = ConfigParser()
            self.config.read(os.path.join(path, "conf", "cfg.ini"))

            if self.config.get("DEFAULT", "mode") == "serial":
                # self.rBtnSerial.setChecked(True)
                self.tabWidget.setCurrentWidget(self.tabSerial)
            if self.config.get("DEFAULT", "mode") == "kafka":
                # self.rBtnKafka.setChecked(True)
                self.tabWidget.setCurrentWidget(self.tabKafka)
            if self.config.get("DEFAULT", "mode") == "manual":
                # self.rBtnManual.setChecked(True)
                self.tabWidget.setCurrentWidget(self.tabManual)

            dict_["kafka_cur_alias"] = \
                self.config.get("DEFAULT", "kafka")
            dict_["kafka_cur_server"] = \
                self.config.get(dict_["kafka_cur_alias"], "server")
            dict_["kafka_cur_topic"] = \
                self.config.get(dict_["kafka_cur_alias"], "topic")
            dict_["kafka_cur_filter"] = \
                self.config.get(dict_["kafka_cur_alias"], "filter")
            self.cbBoxKafkaServer.addItem(
                re.match(r"kafka_(.+)", dict_["kafka_cur_alias"]).group(1))
            self.cbBoxKafkaTopic.addItem(dict_["kafka_cur_topic"])
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
            # self.cbBoxKafkaSshEnable.setCheckState(
            #     Qt.CheckState(2) if config.getboolean(
            #         dict_["kafka_cur_alias"], "ssh_enable") else Qt.CheckState(0))
            self.editKafkaFilter.setText(
                self.config.get(dict_["kafka_cur_alias"], "filter"))

            dict_["serial_cur_cmd"] = self.config.get("DEFAULT", "serial")
            dict_["serial_cur_port"] = \
                self.config.get(dict_["serial_cur_cmd"], "port")
            dict_["serial_cur_filter"] = \
                self.config.get(dict_["serial_cur_cmd"], "filter")

            self.cbBoxSerialPort.addItem(dict_["serial_cur_port"])
            self.cbBoxSerialCmd.addItem(
                re.match(r"serial_(.+)", dict_["serial_cur_cmd"]).group(1))
            self.editSerialFilter.setText(
                self.config.get(dict_["serial_cur_cmd"], "filter"))
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
        self.btnSerialPortRefresh.clicked.connect(
            lambda: self.btnSerialPortRefreshClicked(self.btnSerialPortRefresh))
        self.btnSerialCmdRefresh.clicked.connect(
            lambda: self.btnSerialCmdRefreshClicked(self.btnSerialCmdRefresh))
        self.btnSerialStart.clicked.connect(self.btnSerialStartClicked)
        self.btnSerialStop.clicked.connect(
            lambda: self.btnSerialStopClicked(self.btnSerialStop))
        self.btnKafkaClear.clicked.connect(
            lambda: self.btnClearClicked(self.btnKafkaClear))
        self.btnKafkaServerRefresh.clicked.connect(
            lambda: self.btnKafkaServerRefreshClicked(self.btnKafkaServerRefresh))
        self.btnKafkaTopicRefresh.clicked.connect(
            lambda: self.btnKafkaTopicRefreshClicked(self.btnKafkaTopicRefresh))
        self.btnKafkaStart.clicked.connect(
            lambda: self.btnKafkaStartClicked(self.btnKafkaStart))
        self.btnKafkaStop.clicked.connect(
            lambda: self.btnKafkaStopClicked(self.btnKafkaStop))
        self.btnManualStart.clicked.connect(
            lambda: self.btnManualCheckClicked(self.btnManualStart))
        self.cbBoxSerialPort.currentIndexChanged.connect(
            self.cbBoxSerialPortSelected)
        # self.cbBoxSerialPort.showPopup_.connect(
        #     self.cbBoxSerialPortClicked)
        self.cbBoxSerialCmd.currentIndexChanged.connect(
            self.cbBoxSerialCmdSelected)
        # self.cbBoxSerialCmd.showPopup_.connect(
        #     self.cbBoxSerialCmdClicked)
        # self.cbBoxKafkaCluster.showPopup_.connect(
        #     self.cbBoxKafkaClusterClicked)
        self.cbBoxKafkaServer.currentIndexChanged.connect(
            self.cbBoxKafkaServerSelected)
        # self.cbBoxKafkaTopic.showPopup_.connect(
        #     self.cbBoxKafkaTopicClicked)
        self.cbBoxKafkaTopic.currentIndexChanged.connect(
            self.cbBoxKafkaTopicSelected)
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
        self.tableRes.cellClicked.connect(self.tableResCellClicked)
        self.tableResList.cellClicked.connect(self.tableResListCellClicked)
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
        dict_["cur_row"] = 0

    def btnSerialPortRefreshClicked(self, btn):
        """
        点击清空按钮触发
        :param btn: object
        :return: None
        """
        return self.cbBoxSerialPortClicked()

    def btnSerialCmdRefreshClicked(self, btn):
        """
        点击清空按钮触发
        :param btn: object
        :return: None
        """
        return self.cbBoxSerialCmdClicked()

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
        self.cbBoxSerialPort.setEnabled(False)
        self.editSerialFilter.setEnabled(False)
        self.cbBoxSerialCmd.setEnabled(False)
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
            self.serialThread.serial.stop_read_serial()
            self.serialThread.serial.close()
            self.serialThread.__del__()
        except Exception as e:
            log.error(str(e))

    def btnKafkaServerRefreshClicked(self, btn):
        """
        点击Kafka topic刷新按钮
        :param btn: object
        :return:
        """
        return self.cbBoxKafkaServerClicked()

    def btnKafkaTopicRefreshClicked(self, btn):
        """
        点击Kafka topic刷新按钮
        :param btn: object
        :return:
        """
        return self.cbBoxKafkaTopicClicked()

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
        if not self.cbBoxKafkaTopic.currentText():
            QMessageBox.information(
                self, "提示", "请先选择Server和Topic！", QMessageBox.Ok)
            return

        self.kafkaThread.working = True
        self.kafkaThread.start()
        dict_["cur_row"] = 0
        self.tableResList.clearContents()
        self.tableRes.clearContents()
        self.tableResList.setRowCount(0)
        self.tableRes.setRowCount(0)
        self.btnKafkaStart.setEnabled(False)
        self.cbBoxKafkaServer.setEnabled(False)
        self.cbBoxKafkaTopic.setEnabled(False)
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

    # def btnManualCheckClicked(self, btn):
    #     """
    #     点击手动模式的验证按钮
    #     :param btn: object
    #     :return: None
    #     """
    #     try:
    #         with open(os.path.join(path, "conf", "test.txt")) as f:
    #             data_tmp = f.read()
    #         data = self.editManual.toPlainText() \
    #             if self.editManual.toPlainText().strip() else data_tmp
    #         log.info("Mock log data: " + data)
    #         test = LogCheck()
    #         res = test.check_log(data)
    #         if res:
    #             dict_["cur_row"] = 0
    #             self.checkResultReceived(res)
    #         log.info("Mock Check result: " + str(res))
    #     except Exception as e:
    #         log.error(str(e))

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
            proc = subprocess.Popen("java -jar .\\lib\\logdec-cmd-for-json.jar %s" % data,
                                    stdout=subprocess.PIPE, shell=True)
            (out, err) = proc.communicate()
            log.info("Mock log data: " + str(out))
            test = LogCheck()
            res = test.check_log(str(out))
            if res:
                dict_["cur_row"] = 0
                self.checkResultReceived(res)
            log.info("Mock Check result: " + str(res))
        except Exception as e:
            log.error(str(e))

    def cbBoxKafkaSshEnableChanged(self, i):
        """
        SSH启用状态修改
        :param i: object
        :return: None
        """
        if not self.checkBoxKafkaSshEnable.checkState():
            self.groupBoxSshHeader.setEnabled(False)
            self.config.set(dict_["kafka_cur_alias"], "ssh_enable", "false")
        else:
            self.groupBoxSshHeader.setEnabled(True)
            self.config.set(dict_["kafka_cur_alias"], "ssh_enable", "true")

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

    def cbBoxSerialPortSelected(self, i):
        """
        下拉框选择端口触发
        :param i: QComboBox
        :return: None
        """
        try:
            if not self.cbBoxSerialPort.currentText():
                return
            dict_["serial_cur_port"] = re.findall(
                r"COM[0-9]+", self.cbBoxSerialPort.currentText())[0]
            if dict_["serial_cur_cmd"]:
                self.config.set(dict_["serial_cur_cmd"],
                                "port", dict_["serial_cur_port"])
        except Exception as e:
            log.error(str(e))

    def cbBoxSerialPortClicked(self):
        """
        点击下拉框
        :return: None
        """
        self.cbBoxSerialPort.clear()
        try:
            portList = Serial.get_port_list()
            if portList:
                for i in portList:
                    self.cbBoxSerialPort.addItem(i[0])
        except Exception as e:
            log.error(str(e))
            QMessageBox.information(self, "提示", str(e), QMessageBox.Ok)

    def cbBoxSerialCmdSelected(self, i):
        """
        下拉框选择串口命令触发
        :param i: QComboBox
        :return: None
        """
        try:
            if self.cbBoxSerialCmd.currentText():
                dict_["serial_cur_cmd"] = "serial_" + self.cbBoxSerialCmd.currentText()
                self.config.set("DEFAULT", "serial", dict_["serial_cur_cmd"])
        except Exception as e:
            log.error(str(e))

    def cbBoxSerialCmdClicked(self):
        """
        点击串口命令下拉框
        :return: None
        """
        try:
            self.cbBoxSerialCmd.clear()
            for i in self.config.sections():
                match = re.match(r"^serial_(.+)", i)
                if match:
                    self.cbBoxSerialCmd.addItem(match.group(1))
        except Exception as e:
            log.error(str(e))
            QMessageBox.information(self, "提示", str(e), QMessageBox.Ok)

    def cbBoxKafkaTopicClicked(self):
        """
        点击kafka topic下拉框
        :return:
        """
        try:
            self.cbBoxKafkaTopic.clear()

            if not self.config.get(dict_["kafka_cur_alias"], "group_id"):
                self.config.set(dict_["kafka_cur_alias"], "group_id", gethostname())
            kafka_config = {
                "server": dict_["kafka_cur_server"],
                "group_id": self.config.get(dict_["kafka_cur_alias"], "group_id")
            }
            ssh_config = {
                "host": self.config.get(dict_["kafka_cur_alias"], "ssh_host"),
                "port": self.config.get(dict_["kafka_cur_alias"], "ssh_port"),
                "user": self.config.get(dict_["kafka_cur_alias"], "ssh_user"),
                "pwd": self.config.get(dict_["kafka_cur_alias"], "ssh_pwd")
            } if self.config.getboolean(dict_["kafka_cur_alias"], "ssh_enable") else None

            self.kafka = Kafka(kafka_config=kafka_config, ssh_config=ssh_config)
            self.kafka.init_kafka()
            self.kafka_topics = list(self.kafka.topics_kafka())
            log.info(str(self.kafka_topics))
            if self.kafka_topics:
                self.kafka_topics.sort()
                for i in self.kafka_topics:
                    if re.match(r"^json\..+", i):
                        self.cbBoxKafkaTopic.addItem(str(i))
            self.kafka.stop_kafka()
        except Exception as e:
            log.error(str(e))
            QMessageBox.information(self, "提示", "获取Topic失败，请检查配置文件！", QMessageBox.Ok)

    def cbBoxKafkaTopicSelected(self, i):
        """
        选择kafka topic
        :param i: object
        :return: None
        """
        # self.comboBoxKafkaTopic.setCurrentText("test")
        # dict_["kafka_cur_topic"] = "test"
        dict_["kafka_cur_topic"] = self.cbBoxKafkaTopic.currentText()
        self.config.set(dict_["kafka_cur_alias"], "topic", dict_["kafka_cur_topic"])

    def cbBoxKafkaServerClicked(self):
        """
        点击kafka bootstrap server下拉框
        :return: None
        """
        self.cbBoxKafkaServer.clear()
        try:
            for i in self.config.sections():
                match = re.match(r"^kafka_(.+)", i)
                if match:
                    self.cbBoxKafkaServer.addItem(match.group(1))
        except Exception as e:
            log.error(str(e))

    def cbBoxKafkaServerSelected(self, i):
        """
        选择kafka bootstrap server
        :param i: object
        :return: None
        """
        try:
            if not self.cbBoxKafkaServer.currentText():
                return
            dict_["kafka_cur_alias"] = "kafka_" + self.cbBoxKafkaServer.currentText()
            dict_["kafka_cur_server"] = self.config.get(
                dict_["kafka_cur_alias"], "server")
            self.config.set("DEFAULT", "kafka", dict_["kafka_cur_alias"])

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
                self.config.get(dict_["kafka_cur_alias"], "filter"))
            self.cbBoxKafkaTopic.clear()
            self.cbBoxKafkaTopic.addItem(self.config.get(
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
                self.config.set(dict_["kafka_cur_alias"], "filter", i.text())
            if i is self.editSerialFilter:
                dict_["serial_cur_filter"] = i.text()
                self.config.set(dict_["serial_cur_cmd"], "filter", i.text())
        except Exception as e:
            log.error(str(e))

    def serialStopSignalReceived(self, text):
        """
        Serial子线程结束触发提示
        :param text: str
        :return:
        """
        try:
            self.cbBoxSerialPort.setEnabled(True)
            self.editSerialFilter.setEnabled(True)
            self.cbBoxSerialCmd.setEnabled(True)
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
            self.cbBoxKafkaServer.setEnabled(True)
            self.editKafkaFilter.setEnabled(True)
            self.cbBoxKafkaTopic.setEnabled(True)
            # self.cbBoxKafkaSshEnable.setEnabled(True)
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
            text = self.tableRes.item(row, 2).text()
            if not (re.match(r"^{.*}$", text) or re.match(r"^\[.*\]$", text)):
                return

            data = {}
            o_data = json.loads(text)
            dialog = DialogMore()
            page_total = 0
            if type(o_data) is list:
                page_total = len(o_data)
                data = o_data[0]
            if type(o_data) is dict:
                page_total = 1
                listed_data = list()
                listed_data.append(o_data)
                data = listed_data[0]
            for i in range(page_total):
                dialog.cbBoxPage.addItem(str(i+1))
            dialog.lblTotal.setText("共" + str(page_total) + "组数据")
            dialog.tableResMore.setRowCount(len(data))
            n = 0
            for k in data:
                key_alias = data[k].get("key_alias")
                value = data[k].get("value")
                value_alias = data[k].get("value_alias")
                dialog.tableResMore.setItem(n, 0, QTableWidgetItem(str(k)))
                dialog.tableResMore.item(n, 0).setToolTip(str(k))
                dialog.tableResMore.setItem(n, 1, QTableWidgetItem(str(key_alias) if key_alias else "N/A"))
                dialog.tableResMore.item(n, 1).setToolTip(str(key_alias) if key_alias else "N/A")
                dialog.tableResMore.setItem(n, 2, QTableWidgetItem(str(value) if value else "N/A"))
                dialog.tableResMore.item(n, 2).setToolTip(str(value) if value else "N/A")
                dialog.tableResMore.setItem(n, 3, QTableWidgetItem(str(value_alias) if value_alias else "N/A"))
                dialog.tableResMore.item(n, 3).setToolTip(str(value_alias) if value_alias else "N/A")
                n += 1
            dialog.show()
            dialog.exec_()
        except Exception as e:
            log.error(str(e))
            print(e)


class DialogMore(QDialog, Ui_Dialog):
    def __init__(self):
        super(DialogMore, self).__init__()
        self.setupUi(self)
        self.bind()

    def bind(self):
        self.cbBoxPage.currentIndexChanged.connect(self.cbBoxPageSelected)

    def cbBoxPageSelected(self, i):
        self.tableResMore.clear()
        self.tableResMore.setRowCount()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MyUI()
    main.show()
    sys.exit(app.exec_())
