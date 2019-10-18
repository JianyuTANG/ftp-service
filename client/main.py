import sys
import mainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow
from slots import *


app = QApplication(sys.argv)
MainWindow = QMainWindow()
ui = mainWindow.Ui_MainWindow()
ui.setupUi(MainWindow)
ui.Button_connect.clicked.connect(connect_button)
ui.Button_quit.clicked.connect(quit_button)
ui.Button_browse_local.clicked.connect(browse_button)
ui.Button_mkdir_local.clicked.connect(local_mkdir_button)
ui.Button_rmdir_local.clicked.connect(local_rmdir_button)
ui.Button_refresh_local.clicked.connect(local_refresh_button)
ui.Button_store_local.clicked.connect(store_button)
ui.Button_mkdir_server.clicked.connect(server_mkdir_button)
ui.Button_rmdir_server.clicked.connect(server_rmdir_button)
ui.Button_refresh_server.clicked.connect(server_refresh_button)
ui.Button_rename_server.clicked.connect(server_rename_button)
ui.Button_retrieve_server.clicked.connect(retrieve_button)
MainWindow.show()
sys.exit(app.exec())
