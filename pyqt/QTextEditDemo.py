from PyQt5.QtWidgets import *
import sys

class QTextEditDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('QTextEdit演示')
        self.resize(300,300)

        self.textEdit = QTextEdit()
        self.buttonText = QPushButton('显示文本')
        self.buttonHTML = QPushButton('显示HTML')
        self.buttonToText = QPushButton('获取文本')
        self.buttonToHTML = QPushButton('获取HTML')

        layout = QVBoxLayout()
        
        layout.addWidget(self.textEdit)
        layout.addWidget(self.buttonText)
        layout.addWidget(self.buttonHTML)
        layout.addWidget(self.buttonToText)
        layout.addWidget(self.buttonToHTML)        

        self.setLayout(layout)

        self.buttonText.clicked.connect(self.onClickBtnText)
        self.buttonHTML.clicked.connect(self.onClickBtnHTML)
        self.buttonToText.clicked.connect(self.onClickBtnToText)
        self.buttonToHTML.clicked.connect(self.onClickBtnToHTML)

    def onClickBtnText(self):
        self.textEdit.setPlainText('Hi')

    def onClickBtnToText(self):
        print(self.textEdit.toPlainText())

    def onClickBtnHTML(self):
        self.textEdit.setHtml('<font color="blue" size="5">Hello</font>')

    def onClickBtnToHTML(self):
        print(self.textEdit.toHtml())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = QTextEditDemo()
    main.show()
    sys.exit(app.exec_())