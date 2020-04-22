from PyQt5.QtWidgets import QComboBox
from PyQt5.QtCore import pyqtSignal


class MyComboBox(QComboBox):
    showPopup_ = pyqtSignal()

    def __init__(self):
        super().__init__()

    def showPopup(self):
        self.showPopup_.emit()
        super().showPopup()
