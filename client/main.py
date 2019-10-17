import sys
import mainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow

ui = mainWindow.Ui_MainWindow()
MainWindow = QMainWindow()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
