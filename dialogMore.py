# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialogMore.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(502, 378)
        Dialog.setStyleSheet("* {\n"
"font: 10pt \"Microsoft YaHei UI\";\n"
"}")
        self.btnOk = QtWidgets.QDialogButtonBox(Dialog)
        self.btnOk.setGeometry(QtCore.QRect(130, 330, 341, 32))
        self.btnOk.setOrientation(QtCore.Qt.Horizontal)
        self.btnOk.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.btnOk.setObjectName("btnOk")
        self.tableResMore = QtWidgets.QTableWidget(Dialog)
        self.tableResMore.setGeometry(QtCore.QRect(30, 50, 441, 261))
        self.tableResMore.setObjectName("tableResMore")
        self.tableResMore.setColumnCount(4)
        self.tableResMore.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableResMore.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableResMore.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableResMore.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableResMore.setHorizontalHeaderItem(3, item)
        self.cBoxPage = QtWidgets.QComboBox(Dialog)
        self.cBoxPage.setGeometry(QtCore.QRect(30, 10, 69, 22))
        self.cBoxPage.setObjectName("cBoxPage")
        self.lblTotal = QtWidgets.QLabel(Dialog)
        self.lblTotal.setGeometry(QtCore.QRect(120, 12, 61, 16))
        self.lblTotal.setObjectName("lblTotal")

        self.retranslateUi(Dialog)
        self.btnOk.accepted.connect(Dialog.accept)
        self.btnOk.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "二级数据"))
        item = self.tableResMore.horizontalHeaderItem(0)
        item.setText(_translate("Dialog", "键"))
        item = self.tableResMore.horizontalHeaderItem(1)
        item.setText(_translate("Dialog", "别名"))
        item = self.tableResMore.horizontalHeaderItem(2)
        item.setText(_translate("Dialog", "值"))
        item = self.tableResMore.horizontalHeaderItem(3)
        item.setText(_translate("Dialog", "别名"))
        self.lblTotal.setText(_translate("Dialog", "test"))

