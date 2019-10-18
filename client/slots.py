from client import Client
from main import ui, MainWindow
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
import os
from dialog import input_content, Dialog


client = Client()


def update_prompt():
    data = '\n'.join(client.prompt_lines)
    ui.Prompt.setText(data)


def update_local_filelist():
    directory = client.local_directory
    filelist = os.listdir(directory)
    ui.List_local.clear()
    for i, file in enumerate(filelist):
        ui.List_local.insertItem(i + 1, QtWidgets.QListWidgetItem(file))


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
    update_prompt()


def quit_button():
    if client.connection_status == 'None':
        return
    client.quit()


def browse_button():
    directory = QFileDialog.getExistingDirectory(MainWindow,
                                                "选取文件夹",
                                                "./")
    ui.Line_directory_local.setText(directory)
    client.local_directory = directory
    # TODO update directory list widget
    update_local_filelist()


def local_mkdir_button():
    # TODO add input dialog
    d = Dialog(MainWindow, '请输入新的文件（夹）名')
    d.exec_()
    dirname = input_content
    os.mkdir(os.join(client.local_directory, dirname))
    update_local_filelist()


def server_mkdir_button():
    # TODO add input dialog
    d = Dialog(MainWindow, '请输入新的文件（夹）名')
    d.exec_()
    dirname = input_content
    if client.make_dir(dirname) == 0:
        QtWidgets.QMessageBox.warning(None, 'warning', 'Fail to make dir!')
        return
    # TODO update server file list


def local_rmdir_button():
    dirlist = ui.List_local.selectedItems()
    if len(dirlist) == 0:
        QtWidgets.QMessageBox.warning(None, 'warning', 'Please choose a dir or a file!')
        return
    for d in dirlist:
        p = os.join(client.local_directory, d)
        if os.path.exists(p):
            if os.path.isfile(p):
                os.remove(p)
            else:
                os.removedirs(p)
    update_local_filelist()


def server_rmdir_button():
    dirlist = ui.List_server.selectedItems()
    if len(dirlist) == 0:
        QtWidgets.QMessageBox.warning(None, 'warning', 'Please choose a dir or a file!')
        return
    for d in dirlist:
        if client.remove_dir(d) == 0:
            QtWidgets.QMessageBox.warning(None, 'warning', 'Fail to remove the dir!')
    # TODO update server file list


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
    new_name = input_content
    if client.rename(dirlist[0], new_name) == 0:
        QtWidgets.QMessageBox.warning(None, 'warning', 'Fail to rename the file!')
        return
    # TODO update server file list
