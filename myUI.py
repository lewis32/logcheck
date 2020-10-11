# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'myUI.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 635)
        MainWindow.setMinimumSize(QtCore.QSize(1000, 635))
        MainWindow.setMaximumSize(QtCore.QSize(1000, 635))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/img/assets/icon.ico"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        MainWindow.setWindowIcon(icon)
        MainWindow.setStyleSheet("* {\n"
"font: 10pt \"Microsoft YaHei UI\";\n"
"}\n"
"QToolButton {\n"
"background:transparent;\n"
"}\n"
"QLabel#lblResFailIcon {\n"
"background-color:rgb(255, 99, 71);\n"
"max-width:20px;\n"
"margin:0,0,0,0;\n"
"}\n"
"QLabel#lblResWarnIcon {\n"
"background-color:rgb(255, 215, 0);\n"
"max-width:20px;\n"
"margin:0,0,0,0;\n"
"}\n"
"QLabel#lblResUndefinedIcon {\n"
"background-color:rgb(0, 206, 209);\n"
"max-width:20px;\n"
"margin:0,0,0,0;\n"
"}\n"
"QPushButton{\n"
"max-width:80px;\n"
"}\n"
"QLabel#btnSerialCmdEdit,\n"
"#btnSerialCmdAdd,\n"
"#btnSerialCmdDelete {\n"
"max-width:100px;\n"
"}\n"
"QLabel#btnSerialStart,\n"
"#btnSerialStop,\n"
"#btnSerialClear {\n"
"}")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(20, 10, 661, 171))
        self.tabWidget.setObjectName("tabWidget")
        self.tabSerial = QtWidgets.QWidget()
        self.tabSerial.setObjectName("tabSerial")
        self.gridLayoutWidget_4 = QtWidgets.QWidget(self.tabSerial)
        self.gridLayoutWidget_4.setGeometry(QtCore.QRect(20, 20, 611, 101))
        self.gridLayoutWidget_4.setObjectName("gridLayoutWidget_4")
        self.layoutSerial = QtWidgets.QGridLayout(self.gridLayoutWidget_4)
        self.layoutSerial.setContentsMargins(0, 0, 0, 0)
        self.layoutSerial.setObjectName("layoutSerial")
        self.cbBoxSerialCmd = QtWidgets.QComboBox(self.gridLayoutWidget_4)
        self.cbBoxSerialCmd.setObjectName("cbBoxSerialCmd")
        self.layoutSerial.addWidget(self.cbBoxSerialCmd, 1, 1, 1, 1)
        self.lblSerialCmd = QtWidgets.QLabel(self.gridLayoutWidget_4)
        self.lblSerialCmd.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblSerialCmd.setObjectName("lblSerialCmd")
        self.layoutSerial.addWidget(self.lblSerialCmd, 1, 0, 1, 1)
        self.btnSerialStop = QtWidgets.QPushButton(self.gridLayoutWidget_4)
        self.btnSerialStop.setObjectName("btnSerialStop")
        self.layoutSerial.addWidget(self.btnSerialStop, 1, 5, 1, 1)
        self.btnSerialStart = QtWidgets.QPushButton(self.gridLayoutWidget_4)
        self.btnSerialStart.setObjectName("btnSerialStart")
        self.layoutSerial.addWidget(self.btnSerialStart, 0, 5, 1, 1)
        self.lblSerialPort = QtWidgets.QLabel(self.gridLayoutWidget_4)
        self.lblSerialPort.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblSerialPort.setObjectName("lblSerialPort")
        self.layoutSerial.addWidget(self.lblSerialPort, 0, 0, 1, 1)
        self.lblSerialFilter = QtWidgets.QLabel(self.gridLayoutWidget_4)
        self.lblSerialFilter.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblSerialFilter.setObjectName("lblSerialFilter")
        self.layoutSerial.addWidget(self.lblSerialFilter, 2, 0, 1, 1)
        self.cbBoxSerialPort = QtWidgets.QComboBox(self.gridLayoutWidget_4)
        self.cbBoxSerialPort.setObjectName("cbBoxSerialPort")
        self.layoutSerial.addWidget(self.cbBoxSerialPort, 0, 1, 1, 1)
        self.editSerialFilter = QtWidgets.QLineEdit(self.gridLayoutWidget_4)
        self.editSerialFilter.setObjectName("editSerialFilter")
        self.layoutSerial.addWidget(self.editSerialFilter, 2, 1, 1, 2)
        self.ckBoxSerialDec = QtWidgets.QCheckBox(self.gridLayoutWidget_4)
        self.ckBoxSerialDec.setObjectName("ckBoxSerialDec")
        self.layoutSerial.addWidget(self.ckBoxSerialDec, 2, 3, 1, 1)
        self.btnSerialPortRefresh = QtWidgets.QPushButton(self.gridLayoutWidget_4)
        self.btnSerialPortRefresh.setObjectName("btnSerialPortRefresh")
        self.layoutSerial.addWidget(self.btnSerialPortRefresh, 0, 2, 1, 1)
        self.btnSerialClear = QtWidgets.QPushButton(self.gridLayoutWidget_4)
        self.btnSerialClear.setObjectName("btnSerialClear")
        self.layoutSerial.addWidget(self.btnSerialClear, 2, 5, 1, 1)
        self.btnSerialCmdRefresh = QtWidgets.QPushButton(self.gridLayoutWidget_4)
        self.btnSerialCmdRefresh.setObjectName("btnSerialCmdRefresh")
        self.layoutSerial.addWidget(self.btnSerialCmdRefresh, 1, 2, 1, 1)
        self.layoutSerial.setColumnMinimumWidth(1, 150)
        self.layoutSerial.setColumnMinimumWidth(4, 150)
        self.tabWidget.addTab(self.tabSerial, "")
        self.tabKafka = QtWidgets.QWidget()
        self.tabKafka.setObjectName("tabKafka")
        self.gridLayoutWidget_2 = QtWidgets.QWidget(self.tabKafka)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(20, 20, 611, 101))
        self.gridLayoutWidget_2.setObjectName("gridLayoutWidget_2")
        self.layoutKafka = QtWidgets.QGridLayout(self.gridLayoutWidget_2)
        self.layoutKafka.setContentsMargins(0, 0, 0, 0)
        self.layoutKafka.setObjectName("layoutKafka")
        self.lblKafkaServer = QtWidgets.QLabel(self.gridLayoutWidget_2)
        self.lblKafkaServer.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblKafkaServer.setObjectName("lblKafkaServer")
        self.layoutKafka.addWidget(self.lblKafkaServer, 0, 0, 1, 1)
        self.btnKafkaStop = QtWidgets.QPushButton(self.gridLayoutWidget_2)
        self.btnKafkaStop.setObjectName("btnKafkaStop")
        self.layoutKafka.addWidget(self.btnKafkaStop, 1, 5, 1, 1)
        self.btnKafkaStart = QtWidgets.QPushButton(self.gridLayoutWidget_2)
        self.btnKafkaStart.setObjectName("btnKafkaStart")
        self.layoutKafka.addWidget(self.btnKafkaStart, 0, 5, 1, 1)
        self.btnKafkaClear = QtWidgets.QPushButton(self.gridLayoutWidget_2)
        self.btnKafkaClear.setObjectName("btnKafkaClear")
        self.layoutKafka.addWidget(self.btnKafkaClear, 2, 5, 1, 1)
        self.lblKafkaTopic = QtWidgets.QLabel(self.gridLayoutWidget_2)
        self.lblKafkaTopic.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblKafkaTopic.setObjectName("lblKafkaTopic")
        self.layoutKafka.addWidget(self.lblKafkaTopic, 1, 0, 1, 1)
        self.cbBoxKafkaServer = QtWidgets.QComboBox(self.gridLayoutWidget_2)
        self.cbBoxKafkaServer.setObjectName("cbBoxKafkaServer")
        self.layoutKafka.addWidget(self.cbBoxKafkaServer, 0, 1, 1, 1)
        self.cbBoxKafkaTopic = QtWidgets.QComboBox(self.gridLayoutWidget_2)
        self.cbBoxKafkaTopic.setObjectName("cbBoxKafkaTopic")
        self.layoutKafka.addWidget(self.cbBoxKafkaTopic, 1, 1, 1, 1)
        self.lblKafkaFilter = QtWidgets.QLabel(self.gridLayoutWidget_2)
        self.lblKafkaFilter.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblKafkaFilter.setObjectName("lblKafkaFilter")
        self.layoutKafka.addWidget(self.lblKafkaFilter, 2, 0, 1, 1)
        self.ckBoxKafkaDec = QtWidgets.QCheckBox(self.gridLayoutWidget_2)
        self.ckBoxKafkaDec.setObjectName("ckBoxKafkaDec")
        self.layoutKafka.addWidget(self.ckBoxKafkaDec, 2, 3, 1, 1)
        self.editKafkaFilter = QtWidgets.QLineEdit(self.gridLayoutWidget_2)
        self.editKafkaFilter.setObjectName("editKafkaFilter")
        self.layoutKafka.addWidget(self.editKafkaFilter, 2, 1, 1, 2)
        self.btnKafkaTopicRefresh = QtWidgets.QPushButton(self.gridLayoutWidget_2)
        self.btnKafkaTopicRefresh.setObjectName("btnKafkaTopicRefresh")
        self.layoutKafka.addWidget(self.btnKafkaTopicRefresh, 1, 2, 1, 1)
        self.btnKafkaServerRefresh = QtWidgets.QPushButton(self.gridLayoutWidget_2)
        self.btnKafkaServerRefresh.setObjectName("btnKafkaServerRefresh")
        self.layoutKafka.addWidget(self.btnKafkaServerRefresh, 0, 2, 1, 1)
        self.layoutKafka.setColumnMinimumWidth(1, 150)
        self.layoutKafka.setColumnMinimumWidth(4, 150)
        self.tabWidget.addTab(self.tabKafka, "")
        self.tabManual = QtWidgets.QWidget()
        self.tabManual.setObjectName("tabManual")
        self.gridLayoutWidget_3 = QtWidgets.QWidget(self.tabManual)
        self.gridLayoutWidget_3.setGeometry(QtCore.QRect(20, 20, 611, 108))
        self.gridLayoutWidget_3.setObjectName("gridLayoutWidget_3")
        self.layoutManual = QtWidgets.QGridLayout(self.gridLayoutWidget_3)
        self.layoutManual.setContentsMargins(0, 0, 0, 0)
        self.layoutManual.setSpacing(6)
        self.layoutManual.setObjectName("layoutManual")
        self.ckBoxManualDec = QtWidgets.QCheckBox(self.gridLayoutWidget_3)
        self.ckBoxManualDec.setObjectName("ckBoxManualDec")
        self.layoutManual.addWidget(self.ckBoxManualDec, 1, 2, 1, 1)
        self.editManualFilter = QtWidgets.QLineEdit(self.gridLayoutWidget_3)
        self.editManualFilter.setObjectName("editManualFilter")
        self.layoutManual.addWidget(self.editManualFilter, 1, 1, 1, 1)
        self.btnManualStart = QtWidgets.QPushButton(self.gridLayoutWidget_3)
        self.btnManualStart.setObjectName("btnManualStart")
        self.layoutManual.addWidget(self.btnManualStart, 1, 4, 1, 1)
        self.editManual = QtWidgets.QTextEdit(self.gridLayoutWidget_3)
        self.editManual.setObjectName("editManual")
        self.layoutManual.addWidget(self.editManual, 0, 1, 1, 2)
        self.lblManual = QtWidgets.QLabel(self.gridLayoutWidget_3)
        self.lblManual.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.lblManual.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop|QtCore.Qt.AlignTrailing)
        self.lblManual.setObjectName("lblManual")
        self.layoutManual.addWidget(self.lblManual, 0, 0, 1, 1)
        self.lblManualFilter = QtWidgets.QLabel(self.gridLayoutWidget_3)
        self.lblManualFilter.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.lblManualFilter.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblManualFilter.setObjectName("lblManualFilter")
        self.layoutManual.addWidget(self.lblManualFilter, 1, 0, 1, 1)
        self.layoutManual.setColumnMinimumWidth(3, 150)
        self.tabWidget.addTab(self.tabManual, "")
        self.tabService = QtWidgets.QWidget()
        self.tabService.setObjectName("tabService")
        self.gridLayoutWidget_5 = QtWidgets.QWidget(self.tabService)
        self.gridLayoutWidget_5.setGeometry(QtCore.QRect(20, 20, 611, 101))
        self.gridLayoutWidget_5.setObjectName("gridLayoutWidget_5")
        self.layoutSerial_2 = QtWidgets.QGridLayout(self.gridLayoutWidget_5)
        self.layoutSerial_2.setContentsMargins(0, 0, 0, 0)
        self.layoutSerial_2.setObjectName("layoutSerial_2")
        self.btnSerialStop_2 = QtWidgets.QPushButton(self.gridLayoutWidget_5)
        self.btnSerialStop_2.setObjectName("btnSerialStop_2")
        self.layoutSerial_2.addWidget(self.btnSerialStop_2, 1, 5, 1, 1)
        self.btnSerialStart_2 = QtWidgets.QPushButton(self.gridLayoutWidget_5)
        self.btnSerialStart_2.setObjectName("btnSerialStart_2")
        self.layoutSerial_2.addWidget(self.btnSerialStart_2, 0, 5, 1, 1)
        self.lblSerialPort_2 = QtWidgets.QLabel(self.gridLayoutWidget_5)
        self.lblSerialPort_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblSerialPort_2.setObjectName("lblSerialPort_2")
        self.layoutSerial_2.addWidget(self.lblSerialPort_2, 0, 0, 1, 1)
        self.lblSerialFilter_2 = QtWidgets.QLabel(self.gridLayoutWidget_5)
        self.lblSerialFilter_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblSerialFilter_2.setObjectName("lblSerialFilter_2")
        self.layoutSerial_2.addWidget(self.lblSerialFilter_2, 2, 0, 1, 1)
        self.cbBoxSerialPort_2 = QtWidgets.QComboBox(self.gridLayoutWidget_5)
        self.cbBoxSerialPort_2.setObjectName("cbBoxSerialPort_2")
        self.layoutSerial_2.addWidget(self.cbBoxSerialPort_2, 0, 1, 1, 1)
        self.editSerialFilter_2 = QtWidgets.QLineEdit(self.gridLayoutWidget_5)
        self.editSerialFilter_2.setObjectName("editSerialFilter_2")
        self.layoutSerial_2.addWidget(self.editSerialFilter_2, 2, 1, 1, 2)
        self.ckBoxSerialDec_2 = QtWidgets.QCheckBox(self.gridLayoutWidget_5)
        self.ckBoxSerialDec_2.setObjectName("ckBoxSerialDec_2")
        self.layoutSerial_2.addWidget(self.ckBoxSerialDec_2, 2, 3, 1, 1)
        self.btnSerialPortRefresh_2 = QtWidgets.QPushButton(self.gridLayoutWidget_5)
        self.btnSerialPortRefresh_2.setObjectName("btnSerialPortRefresh_2")
        self.layoutSerial_2.addWidget(self.btnSerialPortRefresh_2, 0, 2, 1, 1)
        self.btnSerialClear_2 = QtWidgets.QPushButton(self.gridLayoutWidget_5)
        self.btnSerialClear_2.setObjectName("btnSerialClear_2")
        self.layoutSerial_2.addWidget(self.btnSerialClear_2, 2, 5, 1, 1)
        self.lblSerialCmd_2 = QtWidgets.QLabel(self.gridLayoutWidget_5)
        self.lblSerialCmd_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblSerialCmd_2.setObjectName("lblSerialCmd_2")
        self.layoutSerial_2.addWidget(self.lblSerialCmd_2, 1, 0, 1, 1)
        self.spinBox = QtWidgets.QSpinBox(self.gridLayoutWidget_5)
        self.spinBox.setMinimum(1024)
        self.spinBox.setSingleStep(1)
        self.spinBox.setProperty("value", 1024)
        self.spinBox.setObjectName("spinBox")
        self.layoutSerial_2.addWidget(self.spinBox, 1, 1, 1, 1)
        self.layoutSerial_2.setColumnMinimumWidth(1, 150)
        self.layoutSerial_2.setColumnMinimumWidth(4, 150)
        self.tabWidget.addTab(self.tabService, "")
        self.gBoxRes = QtWidgets.QGroupBox(self.centralwidget)
        self.gBoxRes.setGeometry(QtCore.QRect(410, 190, 571, 421))
        self.gBoxRes.setObjectName("gBoxRes")
        self.tableRes = QtWidgets.QTableWidget(self.gBoxRes)
        self.tableRes.setGeometry(QtCore.QRect(14, 25, 541, 381))
        self.tableRes.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableRes.setObjectName("tableRes")
        self.tableRes.setColumnCount(4)
        self.tableRes.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableRes.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableRes.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableRes.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableRes.setHorizontalHeaderItem(3, item)
        self.tableRes.horizontalHeader().setDefaultSectionSize(135)
        self.gBoxResList = QtWidgets.QGroupBox(self.centralwidget)
        self.gBoxResList.setGeometry(QtCore.QRect(20, 190, 371, 421))
        self.gBoxResList.setObjectName("gBoxResList")
        self.tableResList = QtWidgets.QTableWidget(self.gBoxResList)
        self.tableResList.setEnabled(True)
        self.tableResList.setGeometry(QtCore.QRect(15, 25, 341, 380))
        self.tableResList.setMinimumSize(QtCore.QSize(341, 380))
        self.tableResList.setMaximumSize(QtCore.QSize(341, 380))
        self.tableResList.setToolTipDuration(-3)
        self.tableResList.setLineWidth(-3)
        self.tableResList.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableResList.setColumnCount(6)
        self.tableResList.setObjectName("tableResList")
        self.tableResList.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableResList.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableResList.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableResList.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableResList.setHorizontalHeaderItem(3, item)
        self.tableResList.horizontalHeader().setDefaultSectionSize(80)
        self.tableResList.horizontalHeader().setMinimumSectionSize(30)
        self.gBoxHint = QtWidgets.QGroupBox(self.centralwidget)
        self.gBoxHint.setGeometry(QtCore.QRect(700, 27, 281, 154))
        self.gBoxHint.setObjectName("gBoxHint")
        self.gridLayoutWidget = QtWidgets.QWidget(self.gBoxHint)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(30, 30, 209, 111))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.layoutHint = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.layoutHint.setContentsMargins(0, 0, 0, 0)
        self.layoutHint.setObjectName("layoutHint")
        self.btnResListUndefined = QtWidgets.QToolButton(self.gridLayoutWidget)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/img/assets/question_mark.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.btnResListUndefined.setIcon(icon1)
        self.btnResListUndefined.setIconSize(QtCore.QSize(20, 20))
        self.btnResListUndefined.setObjectName("btnResListUndefined")
        self.layoutHint.addWidget(self.btnResListUndefined, 3, 0, 1, 1)
        self.lblResListUndefined = QtWidgets.QLabel(self.gridLayoutWidget)
        self.lblResListUndefined.setObjectName("lblResListUndefined")
        self.layoutHint.addWidget(self.lblResListUndefined, 3, 1, 1, 1)
        self.lblResFailIcon = QtWidgets.QLabel(self.gridLayoutWidget)
        self.lblResFailIcon.setEnabled(True)
        self.lblResFailIcon.setMaximumSize(QtCore.QSize(20, 20))
        self.lblResFailIcon.setText("")
        self.lblResFailIcon.setObjectName("lblResFailIcon")
        self.layoutHint.addWidget(self.lblResFailIcon, 1, 2, 1, 1)
        self.btnResListPass = QtWidgets.QToolButton(self.gridLayoutWidget)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/img/assets/check_mark.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.btnResListPass.setIcon(icon2)
        self.btnResListPass.setIconSize(QtCore.QSize(20, 20))
        self.btnResListPass.setObjectName("btnResListPass")
        self.layoutHint.addWidget(self.btnResListPass, 0, 0, 1, 1)
        self.btnResListFail = QtWidgets.QToolButton(self.gridLayoutWidget)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/img/assets/cross_mark.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.btnResListFail.setIcon(icon3)
        self.btnResListFail.setIconSize(QtCore.QSize(20, 20))
        self.btnResListFail.setObjectName("btnResListFail")
        self.layoutHint.addWidget(self.btnResListFail, 1, 0, 1, 1)
        self.lblResListFail = QtWidgets.QLabel(self.gridLayoutWidget)
        self.lblResListFail.setObjectName("lblResListFail")
        self.layoutHint.addWidget(self.lblResListFail, 1, 1, 1, 1)
        self.btnResListWarn = QtWidgets.QToolButton(self.gridLayoutWidget)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/img/assets/exclamation_mark.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.btnResListWarn.setIcon(icon4)
        self.btnResListWarn.setIconSize(QtCore.QSize(20, 20))
        self.btnResListWarn.setObjectName("btnResListWarn")
        self.layoutHint.addWidget(self.btnResListWarn, 2, 0, 1, 1)
        self.lblResListPass = QtWidgets.QLabel(self.gridLayoutWidget)
        self.lblResListPass.setObjectName("lblResListPass")
        self.layoutHint.addWidget(self.lblResListPass, 0, 1, 1, 1)
        self.lblResListWarn = QtWidgets.QLabel(self.gridLayoutWidget)
        self.lblResListWarn.setObjectName("lblResListWarn")
        self.layoutHint.addWidget(self.lblResListWarn, 2, 1, 1, 1)
        self.lblResFail = QtWidgets.QLabel(self.gridLayoutWidget)
        self.lblResFail.setObjectName("lblResFail")
        self.layoutHint.addWidget(self.lblResFail, 1, 3, 1, 1)
        self.lblResWarnIcon = QtWidgets.QLabel(self.gridLayoutWidget)
        self.lblResWarnIcon.setMaximumSize(QtCore.QSize(20, 20))
        self.lblResWarnIcon.setText("")
        self.lblResWarnIcon.setObjectName("lblResWarnIcon")
        self.layoutHint.addWidget(self.lblResWarnIcon, 2, 2, 1, 1)
        self.lblResWarn = QtWidgets.QLabel(self.gridLayoutWidget)
        self.lblResWarn.setObjectName("lblResWarn")
        self.layoutHint.addWidget(self.lblResWarn, 2, 3, 1, 1)
        self.lblResUndefinedIcon = QtWidgets.QLabel(self.gridLayoutWidget)
        self.lblResUndefinedIcon.setMaximumSize(QtCore.QSize(20, 20))
        self.lblResUndefinedIcon.setText("")
        self.lblResUndefinedIcon.setObjectName("lblResUndefinedIcon")
        self.layoutHint.addWidget(self.lblResUndefinedIcon, 3, 2, 1, 1)
        self.lblResUndefined = QtWidgets.QLabel(self.gridLayoutWidget)
        self.lblResUndefined.setObjectName("lblResUndefined")
        self.layoutHint.addWidget(self.lblResUndefined, 3, 3, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1000, 25))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(3)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "日志验证工具 v1.4"))
        self.lblSerialCmd.setText(_translate("MainWindow", "执行命令"))
        self.btnSerialStop.setText(_translate("MainWindow", "停止"))
        self.btnSerialStart.setText(_translate("MainWindow", "开始"))
        self.lblSerialPort.setText(_translate("MainWindow", "串口端口"))
        self.lblSerialFilter.setText(_translate("MainWindow", "过滤词"))
        self.editSerialFilter.setPlaceholderText(_translate("MainWindow", "如特定事件码，支持正则"))
        self.ckBoxSerialDec.setText(_translate("MainWindow", "开启解密"))
        self.btnSerialPortRefresh.setText(_translate("MainWindow", "刷新"))
        self.btnSerialClear.setText(_translate("MainWindow", "清空"))
        self.btnSerialCmdRefresh.setText(_translate("MainWindow", "刷新"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabSerial), _translate("MainWindow", "串口模式"))
        self.lblKafkaServer.setText(_translate("MainWindow", "服务器"))
        self.btnKafkaStop.setText(_translate("MainWindow", "停止"))
        self.btnKafkaStart.setText(_translate("MainWindow", "开始"))
        self.btnKafkaClear.setText(_translate("MainWindow", "清空"))
        self.lblKafkaTopic.setText(_translate("MainWindow", "topic"))
        self.lblKafkaFilter.setText(_translate("MainWindow", "过滤词"))
        self.ckBoxKafkaDec.setText(_translate("MainWindow", "开启解密"))
        self.editKafkaFilter.setPlaceholderText(_translate("MainWindow", "如特定设备id、事件码，支持正则"))
        self.btnKafkaTopicRefresh.setText(_translate("MainWindow", "刷新"))
        self.btnKafkaServerRefresh.setText(_translate("MainWindow", "刷新"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabKafka), _translate("MainWindow", "Kafka模式"))
        self.ckBoxManualDec.setText(_translate("MainWindow", "开启解密"))
        self.editManualFilter.setPlaceholderText(_translate("MainWindow", "如特定事件码，支持正则"))
        self.btnManualStart.setText(_translate("MainWindow", "验证"))
        self.editManual.setPlaceholderText(_translate("MainWindow", "支持多条数据解析"))
        self.lblManual.setText(_translate("MainWindow", "日志数据"))
        self.lblManualFilter.setText(_translate("MainWindow", "过滤词"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabManual), _translate("MainWindow", "手动模式"))
        self.btnSerialStop_2.setText(_translate("MainWindow", "停止"))
        self.btnSerialStart_2.setText(_translate("MainWindow", "开始"))
        self.lblSerialPort_2.setText(_translate("MainWindow", "IP"))
        self.lblSerialFilter_2.setText(_translate("MainWindow", "过滤词"))
        self.editSerialFilter_2.setPlaceholderText(_translate("MainWindow", "如特定事件码，支持正则"))
        self.ckBoxSerialDec_2.setText(_translate("MainWindow", "开启解密"))
        self.btnSerialPortRefresh_2.setText(_translate("MainWindow", "刷新"))
        self.btnSerialClear_2.setText(_translate("MainWindow", "清空"))
        self.lblSerialCmd_2.setText(_translate("MainWindow", "端口"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabService), _translate("MainWindow", "服务模式"))
        self.gBoxRes.setTitle(_translate("MainWindow", "一级数据"))
        item = self.tableRes.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "键"))
        item = self.tableRes.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "别名"))
        item = self.tableRes.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "值"))
        item = self.tableRes.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "别名"))
        self.gBoxResList.setTitle(_translate("MainWindow", "验证结果"))
        item = self.tableResList.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "上级事件"))
        item = self.tableResList.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "本级事件"))
        item = self.tableResList.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "别名"))
        item = self.tableResList.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "结果"))
        self.gBoxHint.setTitle(_translate("MainWindow", "图例"))
        self.btnResListUndefined.setText(_translate("MainWindow", "..."))
        self.lblResListUndefined.setText(_translate("MainWindow", "未定义"))
        self.btnResListPass.setText(_translate("MainWindow", "..."))
        self.btnResListFail.setText(_translate("MainWindow", "..."))
        self.lblResListFail.setText(_translate("MainWindow", "异常"))
        self.btnResListWarn.setText(_translate("MainWindow", "..."))
        self.lblResListPass.setText(_translate("MainWindow", "正常"))
        self.lblResListWarn.setText(_translate("MainWindow", "告警"))
        self.lblResFail.setText(_translate("MainWindow", "值与正则不符"))
        self.lblResWarn.setText(_translate("MainWindow", "键有定义但未上报"))
        self.lblResUndefined.setText(_translate("MainWindow", "键有上报但未定义"))

import assets_rc
