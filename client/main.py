import sys
import mainWindow
from client import Client
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem, QApplication, QMainWindow, QMessageBox
import os
from dialog import Dialog
import shutil
from multi_thread import MyThread


client = Client()
app = QApplication(sys.argv)
MainWindow = QMainWindow()
ui = mainWindow.Ui_MainWindow()
ui.setupUi(MainWindow)
ui.Input_port.setText('10011')
ui.Input_ip.setText('127.0.0.1')
ui.Input_username.setText('anonymous')
ui.Input_password.setText('e73jzTRTNqCN9PYAAjjn')

ui.Tasks.setColumnCount(3)
ui.Tasks.setHorizontalHeaderLabels(['文件名', '任务类型', '状态'])
task_num = 0
t = MyThread()


def update_prompt():
    data = '\n'.join(client.prompt_lines)
    ui.Prompt.setText(data)


t.update_prompt_signal.connect(update_prompt)


def move_end():
    ui.Prompt.moveCursor(QtGui.QTextCursor.End)


ui.Prompt.textChanged.connect(move_end)


def set_task(i, name, ti, status):
    row_num = ui.Tasks.rowCount()
    if i == row_num:
        ui.Tasks.insertRow(row_num)
    elif i > row_num:
        return 0
    ui.Tasks.setItem(i, 0, QTableWidgetItem(name))
    ui.Tasks.setItem(i, 1, QTableWidgetItem(ti))
    ui.Tasks.setItem(i, 2, QTableWidgetItem(status))
    return 1


t.set_task_signal.connect(set_task)


def update_local_filelist():
    directory = client.local_directory
    filelist = os.listdir(directory)
    ui.List_local.clear()
    ui.Line_directory_local.setText(directory)
    for i, file in enumerate(filelist):
        ui.List_local.insertItem(i + 1, QtWidgets.QListWidgetItem(file))


t.update_local_list_signal.connect(update_local_filelist)


def update_server_filelist():
    if ui.radio_pasv.isChecked():
        client.mode = 'PASV'
    else:
        client.mode = 'PORT'
    print('start list')
    if client.list_server() == 0:
        update_prompt()
        QtWidgets.QMessageBox.warning(None, 'warning', 'Fail to LIST!')
        return
    update_prompt()
    ui.List_server.clear()
    ui.List_server.insertItem(1, QtWidgets.QListWidgetItem('..'))
    for i, file in enumerate(client.server_file_list):
        ui.List_server.insertItem(i + 2, QtWidgets.QListWidgetItem(file))


t.update_server_list_signal.connect(update_server_filelist)


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
    update_server_filelist()
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
    tgt = os.path.join(client.local_directory, currentdir)
    if os.path.isdir(tgt):
        client.local_directory = tgt
        update_local_filelist()


def server_chdir_event():
    if client.connection_status == 'None':
        QtWidgets.QMessageBox.warning(None, 'warning', 'Please connect first!')
        return
    if client.transmitting_status != 'None':
        QtWidgets.QMessageBox.warning(None, 'warning', 'Now transmitting, please wait!')
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
    if client.transmitting_status != 'None':
        QtWidgets.QMessageBox.warning(None, 'warning', 'Now transmitting, please wait!')
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
    if client.transmitting_status != 'None':
        QtWidgets.QMessageBox.warning(None, 'warning', 'Now transmitting, please wait!')
        return
    dirlist = ui.List_server.selectedItems()
    if len(dirlist) == 0:
        QtWidgets.QMessageBox.warning(None, 'warning', 'Please choose a dir or a file!')
        return
    for d in dirlist:
        d = d.text()
        if client.remove_dir(d) == 0:
            QtWidgets.QMessageBox.warning(None, 'warning', 'Fail to remove the dir!')
    # TODO update server file list
    update_prompt()
    update_server_filelist()


def server_rename_button():
    if client.connection_status == 'None':
        QtWidgets.QMessageBox.warning(None, 'warning', 'Please connect first!')
        return
    if client.transmitting_status != 'None':
        QtWidgets.QMessageBox.warning(None, 'warning', 'Now transmitting, please wait!')
        return
    dirlist = ui.List_server.selectedItems()
    if len(dirlist) != 1:
        QtWidgets.QMessageBox.warning(None, 'warning', 'Please only choose one dir or one file!')
        return
    d = Dialog(MainWindow, '请输入新的文件（夹）名')
    d.exec_()
    new_name = d.get_name()
    print(new_name)
    if client.rename(dirlist[0].text(), new_name) == 0:
        update_prompt()
        QtWidgets.QMessageBox.warning(None, 'warning', 'Fail to rename the file!')
        return
    update_server_filelist()
    update_prompt()
    # TODO update server file list


def local_refresh_button():
    update_local_filelist()


def server_refresh_button():
    if client.connection_status == 'None':
        QtWidgets.QMessageBox.warning(None, 'warning', 'Please connect first!')
        return
    if client.transmitting_status != 'None':
        QtWidgets.QMessageBox.warning(None, 'warning', 'Now transmitting, please wait!')
        return
    update_server_filelist()


def retrieve_button():
    if client.connection_status == 'None':
        QtWidgets.QMessageBox.warning(None, 'warning', 'Please connect first!')
        return
    if client.transmitting_status != 'None':
        QtWidgets.QMessageBox.warning(None, 'warning', 'Now transmitting, please wait!')
        return
    dirlist = ui.List_server.selectedItems()
    if len(dirlist) != 1:
        QtWidgets.QMessageBox.warning(None, 'warning', 'Please choose one file!')
        return
    filename = dirlist[0].text()
    offset = 0
    if os.path.isfile(os.path.join(client.local_directory, filename)):
        ret = QMessageBox.question(MainWindow,
                                   "是否断点续传",
                                   "文件已在本地存在，是否断点续传?",
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        if ret == QMessageBox.Yes:
            filesize = os.path.getsize(os.path.join(client.local_directory, filename))
            if client.send_REST(filesize):
                offset = filesize

    global task_num
    seq = task_num
    task_num += 1
    set_task(seq, filename, 'RETRIEVE', '传输中')
    QApplication.processEvents()
    if ui.radio_pasv.isChecked():
        client.mode = 'PASV'
    else:
        client.mode = 'PORT'
    '''
    if client.retrieve_file(filename) == 0:
        set_task(seq, filename, 'RETRIEVE', '失败')
        update_prompt()
        QtWidgets.QMessageBox.warning(None, 'warning', 'Fail to retrieve the file!')
        return
    update_prompt()
    set_task(seq, filename, 'RETRIEVE', '已完成')
    update_local_filelist()
    '''
    args = (filename, seq, offset)
    t.set_func_agrs(receive_file, args)
    try:
        t.start()
    except:
        print('555')


def receive_file(args, signal, signal1, signal2, signal3):
    print('start retrieve')
    filename = args[0]
    seq = args[1]
    client.offset = args[2]
    if client.retrieve_file(filename) == 0:
        signal1.emit(seq, filename, 'RETRIEVE', '失败')
        signal.emit()
        QtWidgets.QMessageBox.warning(None, 'warning', 'Fail to retrieve the file!')
        return
    signal.emit()
    signal1.emit(seq, filename, 'RETRIEVE', '已完成')
    signal2.emit()
    client.offset = 0


def store_button():
    if client.connection_status == 'None':
        QtWidgets.QMessageBox.warning(None, 'warning', 'Please connect first!')
        return
    if client.transmitting_status != 'None':
        QtWidgets.QMessageBox.warning(None, 'warning', 'Now transmitting, please wait!')
        return
    dirlist = ui.List_local.selectedItems()
    if len(dirlist) != 1:
        QtWidgets.QMessageBox.warning(None, 'warning', 'Please choose one file!')
        return
    local_filename = dirlist[0].text()
    d = Dialog(MainWindow, '请输入保存至服务器的文件名')
    d.exec_()
    new_filename = d.get_name()
    global task_num
    seq = task_num
    task_num += 1
    set_task(seq, local_filename, 'STORE', '传输中')
    QApplication.processEvents()
    if ui.radio_pasv.isChecked():
        client.mode = 'PASV'
    else:
        client.mode = 'PORT'
    args = (local_filename, new_filename, seq)
    t.set_func_agrs(send_file, args)
    t.start()
    '''
    if client.store_file(local_filename, new_filename) == 0:
        update_prompt()
        set_task(seq, local_filename, 'STORE', '失败')
        QtWidgets.QMessageBox.warning(None, 'warning', 'Fail to store the file!')
        return
    update_prompt()
    set_task(seq, local_filename, 'STORE', '已完成')
    update_server_filelist()
    '''


def send_file(args, signal, signal1, signal2, signal3):
    local_filename = args[0]
    new_filename = args[1]
    seq = args[2]
    if client.store_file(local_filename, new_filename) == 0:
        signal.emit()
        signal1.emit(seq, local_filename, 'STORE', '失败')
        QtWidgets.QMessageBox.warning(None, 'warning', 'Fail to store the file!')
        return
    signal.emit()
    signal1.emit(seq, local_filename, 'STORE', '已完成')
    signal3.emit()


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
