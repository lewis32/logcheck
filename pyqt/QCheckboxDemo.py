from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import sys

class QCheckboxDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('复选框控件demo')

        layout = QHBoxLayout()

        self.checkbox1 = QCheckBox('复选框控件1')
        self.checkbox1.setChecked(True)
        self.checkbox1.stateChanged.connect(lambda:self.checkboxStatus(self.checkbox1))

        self.checkbox2 = QCheckBox('复选框控件2')
        self.checkbox2.stateChanged.connect(lambda:self.checkboxStatus(self.checkbox2))

        self.checkbox3 = QCheckBox('复选框控件3')
        self.checkbox3.stateChanged.connect(lambda:self.checkboxStatus(self.checkbox3))
        self.checkbox3.setTristate(True)
        self.checkbox3.setCheckState(Qt.PartiallyChecked)

        layout.addWidget(self.checkbox1)
        layout.addWidget(self.checkbox2)
        layout.addWidget(self.checkbox3)
        self.setLayout(layout)


    def checkboxStatus(self,cb):
        checkbox1status =  self.checkbox1.text() + \
            ', isChecked= ' + \
            str(self.checkbox1.isChecked()) + \
            ', checkStatus=' + \
            str(self.checkbox1.checkState()) + '\n'
        checkbox2status =  self.checkbox2.text() + \
            ', isChecked= ' + \
            str(self.checkbox2.isChecked()) + \
            ', checkStatus=' + \
            str(self.checkbox2.checkState()) + '\n'
        checkbox3status =  self.checkbox3.text() + \
            ', isChecked= ' + \
            str(self.checkbox3.isChecked()) + \
            ', checkStatus=' + \
            str(self.checkbox3.checkState()) + '\n'

        print(checkbox1status + checkbox2status + checkbox3status)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = QCheckboxDemo()
    main.show()
    sys.exit(app.exec_())