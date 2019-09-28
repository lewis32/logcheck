from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import sys

class QComboBoxDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('下拉列表')
        self.resize(300,100)
        layout = QVBoxLayout()

        self.label = QLabel('选择语言')

        self.cb = QComboBox()
        self.cb.addItem('C++')
        self.cb.addItem('Python')
        self.cb.addItem('Java')

        self.cb.currentIndexChanged.connect(self.selectionChange)

        layout.addWidget(self.label)
        layout.addWidget(self.cb)
        self.setLayout(layout)

    def selectionChange(self,i):
        self.label.setText(self.cb.currentText())
        self.label.adjustSize()

        for cnt in range(self.cb.count()):
            print('item' + str(cnt) + '=' + self.cb.itemText(cnt))
        print('current index',i,'selection changed',self.cb.currentText())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = QComboBoxDemo()
    main.show()
    sys.exit(app.exec_())