from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt
import inputDialog


input_content = ''


class Dialog(QDialog):
    def __init__(self, parent=None, hintmsg=''):
        super().__init__(parent)
        self.dialog_ui = inputDialog.Ui_Dialog()
        self.dialog_ui.setupUi(self)
        self.dialog_ui.label.setText(hintmsg)
        self.setWindowTitle('输入')
        input_content = ''
        self.setWindowModality(Qt.ApplicationModal)
        self.dialog_ui.okbutton.clicked.connect(self.clicked)


    def clicked(self):
        input_content = self.dialog_ui.Input.text()
        self.accept()
