from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt
import inputDialog


class Dialog(QDialog):
    def __init__(self, parent=None, hintmsg=''):
        super().__init__(parent)
        self.dialog_ui = inputDialog.Ui_Dialog()
        self.dialog_ui.setupUi(self)
        self.setWindowTitle('输入')
        self.dialog_ui.label.setText(hintmsg)
        self.dialog_ui.okbutton.clicked.connect(self.accept)
        # self.setWindowModality(Qt.ApplicationModal)

    def get_name(self):
        # return '666'
        return self.dialog_ui.Input.text()
