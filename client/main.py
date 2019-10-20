import sys
import mainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow
from client import Client
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
import os
from dialog import Dialog
import shutil

client = Client()
app = QApplication(sys.argv)
MainWindow = QMainWindow()
ui = mainWindow.Ui_MainWindow()
ui.setupUi(MainWindow)
ui.Input_port.setText('10011')
ui.Input_ip.setText('127.0.0.1')
ui.Input_username.setText('anonymous')
ui.Input_password.setText('e73jzTRTNqCN9PYAAjjn')


def update_prompt():
    data = '\n'.join(client.prompt_lines)
    print(data)
    ui.Prompt.setText(data)


def update_local_filelist():
    directory = client.local_directory
    filelist = os.listdir(directory)
    ui.List_local.clear()
    ui.Line_directory_local.setText(directory)
    for i, file in enumerate(filelist):
        ui.List_local.insertItem(i + 1, QtWidgets.QListWidgetItem(file))


def update_server_filelist():
    if ui.radio_pasv.isChecked():
        client.mode = 'PASV'
    else:
        client.mode = 'PORT'
    if client.list_server() == 0:
        update_prompt()
        QtWidgets.QMessageBox.warning(None, 'warning', 'Fail to LIST!')
        return
    update_prompt()
    ui.List_server.clear()
    for i, file in enumerate(client.server_file_list):
        ui.List_server.insertItem(i + 1, QtWidgets.QListWidgetItem(file))


def connect_button():
    if client.connection_status == 'logged in':
        QtWidgets.QMessageBox.warning(None, 'warning', 'Already connected!')
        return
    username = ui.Input_username.text()
    password = ui.Input_password.text()
    ip = ui.Input_ip.text()
    port = int(ui.Input_port.text())
    client.username = username
    client.password = password
    client.server_ip = ip
    client.server_port = port

    if client.connect() == 0:
        update_prompt()
        QtWidgets.QMessageBox.warning(None, 'warning', 'Fail to connect the server!')
        return
    # TODO update directories
    ui.Line_directory_local.setText(client.local_directory)
    update_local_filelist()
    if client.get_server_directory() == 0:
        update_prompt()
        QtWidgets.QMessageBox.warning(None, 'warning', 'Fail to print the directory!')
        return
    ui.Line_directory_server.setText(client.server_directory)
    update_prompt()


def quit_button():
    if client.connection_status == 'None':
        QtWidgets.QMessageBox.warning(None, 'warning', 'Haven\'t logged in!')
        return
    client.quit()
    update_prompt()


def browse_button():
    ui.Line_directory_local.setText('x')
    directory = QFileDialog.getExistingDirectory(MainWindow,
                                                "选取文件夹",
                                                "./")
    ui.Line_directory_local.setText(directory)
    client.local_directory = directory
    # TODO update directory list widget
    update_local_filelist()


def local_chdir_event():
    print('666')
    dirlist = ui.List_local.selectedItems()
    print('555')
    currentdir = dirlist[0].text()
    print(currentdir)
    client.local_directory = os.path.join(client.local_directory, currentdir)
    update_local_filelist()


def server_chdir_event():
    if client.connection_status == 'None':
        QtWidgets.QMessageBox.warning(None, 'warning', 'Please connect first!')
        return
    dirlist = ui.List_server.selectedItems()
    currentdir = dirlist[0].text()
    if client.change_dir(currentdir) == 0:
        update_prompt()
        QtWidgets.QMessageBox.warning(None, 'warning', 'Fail to change the dir!')
        return
    if client.get_server_directory() == 0:
        update_prompt()
        QtWidgets.QMessageBox.warning(None, 'warning', 'Fail to print the directory!')
        return
    ui.Line_directory_server.setText(client.server_directory)
    update_server_filelist()
    update_prompt()


def local_mkdir_button():
    # TODO add input dialog
    dia = Dialog(parent=MainWindow, hintmsg='please enter the name of the dir')
    result = dia.exec_()
    dirname = dia.get_name()
    os.mkdir(os.path.join(client.local_directory, dirname))
    update_local_filelist()


def server_mkdir_button():
    if client.connection_status == 'None':
        QtWidgets.QMessageBox.warning(None, 'warning', 'Please connect first!')
        return
    # TODO add input dialog
    d = Dialog(MainWindow, '请输入新的文件（夹）名')
    d.exec_()
    dirname = d.get_name()
    if client.make_dir(dirname) == 0:
        update_prompt()
        QtWidgets.QMessageBox.warning(None, 'warning', 'Fail to make dir!')
        return
    # TODO update server file list
    update_server_filelist()


def local_rmdir_button():
    dirlist = ui.List_local.selectedItems()
    if len(dirlist) == 0:
        QtWidgets.QMessageBox.warning(None, 'warning', 'Please choose a dir or a file!')
        return
    for d in dirlist:
        d = d.text()
        p = os.path.join(client.local_directory, d)
        if os.path.exists(p):
            if os.path.isfile(p):
                os.remove(p)
            else:
                shutil.rmtree(p)
    update_local_filelist()


def server_rmdir_button():
    if client.connection_status == 'None':
        QtWidgets.QMessageBox.warning(None, 'warning', 'Please connect first!')
        return
    dirlist = ui.List_server.selectedItems()
    if len(dirlist) == 0:
        QtWidgets.QMessageBox.warning(None, 'warning', 'Please choose a dir or a file!')
        return
    for d in dirlist:
        if client.remove_dir(d) == 0:
            QtWidgets.QMessageBox.warning(None, 'warning', 'Fail to remove the dir!')
    # TODO update server file list
    update_prompt()
    update_server_filelist()


def server_rename_button():
    if client.connection_status == 'None':
        QtWidgets.QMessageBox.warning(None, 'warning', 'Please connect first!')
        return
    dirlist = ui.List_server.selectedItems()
    if len(dirlist) != 1:
        QtWidgets.QMessageBox.warning(None, 'warning', 'Please only choose one dir or one file!')
        return
    d = Dialog(MainWindow, '请输入新的文件（夹）名')
    d.exec_()
    new_name = d.get_name()
    if client.rename(dirlist[0], new_name) == 0:
        update_prompt()
        QtWidgets.QMessageBox.warning(None, 'warning', 'Fail to rename the file!')
        return
    # TODO update server file list


def local_refresh_button():
    update_local_filelist()


def server_refresh_button():
    if client.connection_status == 'None':
        QtWidgets.QMessageBox.warning(None, 'warning', 'Please connect first!')
        return
    update_server_filelist()


def retrieve_button():
    if client.connection_status == 'None':
        QtWidgets.QMessageBox.warning(None, 'warning', 'Please connect first!')
        return
    dirlist = ui.List_local.selectedItems()
    if len(dirlist) != 1:
        QtWidgets.QMessageBox.warning(None, 'warning', 'Please choose one file!')
        return
    filename = dirlist[0]
    if ui.radio_pasv.isChecked():
        client.mode = 'PASV'
    else:
        client.mode = 'PORT'
    if client.retrieve_file(filename) == 0:
        update_prompt()
        QtWidgets.QMessageBox.warning(None, 'warning', 'Fail to retrieve the file!')
        return
    update_prompt()
    update_local_filelist()


def store_button():
    if client.connection_status == 'None':
        QtWidgets.QMessageBox.warning(None, 'warning', 'Please connect first!')
        return
    dirlist = ui.List_local.selectedItems()
    if len(dirlist) != 1:
        QtWidgets.QMessageBox.warning(None, 'warning', 'Please choose one file!')
        return
    local_filename = dirlist[0]
    d = Dialog(MainWindow, '请输入保存至服务器的文件名')
    d.exec_()
    new_filename = d.get_name()
    if ui.radio_pasv.isChecked():
        client.mode = 'PASV'
    else:
        client.mode = 'PORT'
    if client.store_file(local_filename, new_filename) == 0:
        update_prompt()
        QtWidgets.QMessageBox.warning(None, 'warning', 'Fail to store the file!')
        return
    update_prompt()
    update_server_filelist()



ui.Button_quit.clicked.connect(quit_button)
ui.Button_connect.clicked.connect(connect_button)
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
ui.List_server.doubleClicked.connect(server_chdir_event)
ui.List_local.doubleClicked.connect(local_chdir_event)
MainWindow.show()
sys.exit(app.exec())

