# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\Program Files\Sublime\MyWork\logcheck\logcheck\core\demo.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridFrame = QtWidgets.QFrame(self.centralwidget)
        self.gridFrame.setGeometry(QtCore.QRect(39, 30, 721, 500))
        self.gridFrame.setObjectName("gridFrame")
        self.gridLayout = QtWidgets.QGridLayout(self.gridFrame)
        self.gridLayout.setObjectName("gridLayout")
        self.comboBox = QtWidgets.QComboBox(self.gridFrame)
        self.comboBox.setObjectName("comboBox")
        self.gridLayout.addWidget(self.comboBox, 0, 0, 1, 1)
        self.btn_refresh = QtWidgets.QPushButton(self.gridFrame)
        self.btn_refresh.setObjectName("btn_refresh")
        self.gridLayout.addWidget(self.btn_refresh, 0, 1, 1, 1)
        self.btn_start = QtWidgets.QPushButton(self.gridFrame)
        self.btn_start.setObjectName("btn_start")
        self.gridLayout.addWidget(self.btn_start, 0, 2, 1, 1)
        self.btn_stop = QtWidgets.QPushButton(self.gridFrame)
        self.btn_stop.setObjectName("btn_stop")
        self.gridLayout.addWidget(self.btn_stop, 0, 3, 1, 1)

        # QTableView for result
        self.model = QtGui.QStandardItemModel(2,2)
        self.model.setHorizontalHeaderLabels(['原始数据','校验结果'])
        for row in range(2):
            for column in range(2):
                i=QtGui.QStandardItem('row %s,column %s' % (row,column))
                self.model.setItem(row,column,i)
        self.tableView = QtWidgets.QTableView(self.gridFrame)
        self.tableView.setObjectName("tableView")
        self.tableView.setModel(self.model)
        self.gridLayout.addWidget(self.tableView, 1, 0, 1, 4)
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.btn_refresh.setText(_translate("MainWindow", "刷新"))
        self.btn_start.setText(_translate("MainWindow", "开始对比"))
        self.btn_stop.setText(_translate("MainWindow", "结束对比"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
