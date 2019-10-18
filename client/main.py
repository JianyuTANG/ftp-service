import sys
import mainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow


app = QApplication(sys.argv)
MainWindow = QMainWindow()
ui = mainWindow.Ui_MainWindow()
ui.setupUi(MainWindow)
MainWindow.show()
sys.exit(app.exec())
