from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator,QDoubleValidator,QRegExpValidator
from PyQt5.QtCore import QRegExp
import sys

class QLineEditValidator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('校验器')
        
        formLayout = QFormLayout()

        intLineEdit = QLineEdit()
        floatLineEdit = QLineEdit()
        validatorLineEdit = QLineEdit()

        formLayout.addRow('整数类型', intLineEdit)
        formLayout.addRow('浮点类型', floatLineEdit)
        formLayout.addRow('数字和字母', validatorLineEdit)

        intLineEdit.setPlaceholderText('整形')
        floatLineEdit.setPlaceholderText('浮点型')
        validatorLineEdit.setPlaceholderText('字母和数字')

        intValidator = QIntValidator(self)
        intValidator.setRange(1, 99)
        floatValidator = QDoubleValidator(self)
        floatValidator.setRange(-360, 360)
        floatValidator.setNotation(QDoubleValidator.StandardNotation)
        floatValidator.setDecimals(2)

        reg = QRegExp('[a-zA-Z0-9]+$')
        validator = QRegExpValidator(self)
        validator.setRegExp(reg)

        intLineEdit.setValidator(intValidator)
        floatLineEdit.setValidator(floatValidator)
        validatorLineEdit.setValidator(validator)

        self.setLayout(formLayout)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = QLineEditValidator()
    main.show()
    sys.exit(app.exec_())