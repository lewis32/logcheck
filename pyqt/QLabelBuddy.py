from PyQt5.QtWidgets import *
import sys


class QLabelBuddy(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()
       
    def initUI(self):
        self.setWindowTitle('伙伴控件')

        nameLabel = QLabel('&Name', self)
        nameLineEdit = QLineEdit(self)
        nameLabel.setBuddy(nameLineEdit)

        passwdLabel = QLabel('&Password', self)
        passwdLineEdit = QLineEdit(self)
        passwdLabel.setBuddy(passwdLineEdit)

        btnOK = QPushButton('&OK')
        btnCancel = QPushButton('&Cancel')

        mainLayout = QGridLayout(self)
        mainLayout.addWidget(nameLabel, 0, 0)
        mainLayout.addWidget(nameLineEdit, 0, 1, 1, 2)
        mainLayout.addWidget(passwdLabel, 1, 0)
        mainLayout.addWidget(passwdLineEdit, 1, 1, 1, 2)
        mainLayout.addWidget(btnOK, 2, 1)
        mainLayout.addWidget(btnCancel, 2, 2)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = QLabelBuddy()
    main.show()
    sys.exit(app.exec_())