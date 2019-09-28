from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys

class QRadioButtonDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('QRadioButton Demo')

        layout = QHBoxLayout()
        self.btn1 = QRadioButton('单选按钮1')
        self.btn1.setChecked(True)
        self.btn2 = QRadioButton('单选按钮2')

        self.btn1.toggled.connect(self.btnStatus)
        self.btn2.toggled.connect(self.btnStatus)

        layout.addWidget(self.btn1)
        layout.addWidget(self.btn2)
        self.setLayout(layout)

    def btnStatus(self):
        radioBtn = self.sender()
        if radioBtn.text() == '单选按钮1' or radioBtn.text() == '单选按钮2':
            if radioBtn.isChecked():
                print(radioBtn.text() + '被选中')
            else:
                print(radioBtn.text() + '被取消选中')

        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = QRadioButtonDemo()
    main.show()
    sys.exit(app.exec_())