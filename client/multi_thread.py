from PyQt5.QtCore import pyqtSignal, QThread


class MyThread (QThread):
    update_prompt_signal = pyqtSignal()
    set_task_signal = pyqtSignal(int, str, str, str)
    update_local_list_signal = pyqtSignal()
    update_server_list_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

    def set_func_agrs(self, func, args):
        self.func = func
        self.args = args

    def run(self):
        self.func(self.args, self.update_prompt_signal, self.set_task_signal,
                  self.update_local_list_signal, self.update_server_list_signal)
