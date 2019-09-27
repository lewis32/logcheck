from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
import sys

class QLineEditDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        edit1 = QLineEdit()
        edit1.setValidator(QIntValidator())
        edit1.setMaxLength(4)
        edit1.setFont(QFont('Arial',10))

        edit2 = QLineEdit()
        edit2.setValidator(QDoubleValidator(0.99,99.99,2))

        edit3 = QLineEdit()
        edit3.setInputMask('99-9999-999999;#')

        edit4 = QLineEdit()
        edit4.textChanged.connect(self.textChanged)

        edit5 = QLineEdit()
        edit5.setEchoMode(QLineEdit.Password)
        edit5.editingFinished.connect(self.enterPress)

        edit6 =QLineEdit('Hi')
        edit6.setReadOnly(True)

        formLayout = QFormLayout()
        formLayout.addRow('整数校验',edit1)
        formLayout.addRow('浮点数校验',edit2)
        formLayout.addRow('输入掩码',edit3)
        formLayout.addRow('显示输入',edit4)
        formLayout.addRow('密码',edit5)
        formLayout.addRow('只读',edit6)

        self.setLayout(formLayout)
        self.setWindowTitle('Demo')

    def textChanged(self, text):
        print('输入的内容是 {}'.format(text))
    
    def enterPress(self):
        print('pressed!')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = QLineEditDemo()
    main.show()
    sys.exit(app.exec_())