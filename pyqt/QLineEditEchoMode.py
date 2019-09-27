from PyQt5.QtWidgets import *
import sys

class QLineEditMode(QWidget):
    def __init__(self):
        # super(QLineEditMode,self).__init__()
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('文本输入和回显模式')
        formLayout = QFormLayout()
        normalLineEdit = QLineEdit()
        noEchoLineEdit = QLineEdit()
        passwdLineEdit = QLineEdit()
        passwdEchoOnEditLineEdit = QLineEdit()

        formLayout.addRow('Normal',normalLineEdit)
        formLayout.addRow('NoEcho',noEchoLineEdit)
        formLayout.addRow('Password',passwdLineEdit)
        formLayout.addRow('PasswordEchoOnEdit',passwdEchoOnEditLineEdit)
        
        normalLineEdit.setPlaceholderText('Normal')
        noEchoLineEdit.setPlaceholderText('NoEcho')
        passwdLineEdit.setPlaceholderText('Password')
        passwdEchoOnEditLineEdit.setPlaceholderText('PasswordEchoOnEdit')

        normalLineEdit.setEchoMode(QLineEdit.Normal)
        noEchoLineEdit.setEchoMode(QLineEdit.NoEcho)
        passwdLineEdit.setEchoMode(QLineEdit.Password)
        passwdEchoOnEditLineEdit.setEchoMode(QLineEdit.PasswordEchoOnEdit)

        self.setLayout(formLayout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = QLineEditMode()
    main.show()
    sys.exit(app.exec_())