import os
import socket
import re

pasv_re = re.compile(r'(\d*),(\d*),(\d*),(\d*),(\d*),(\d*)')


class Client:
    def __init__(self):
        self.username = ''
        self.password = ''
        self.server_ip = ''
        self.server_port = 0
        self.transmit_ip = ''
        self.transmit_port = 0
        self.connection_status = 'None'
        self.transmitting_status = 'None'
        self.mode = 'PASV'
        self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.local_directory = os.getcwd()
        self.server_directory = None
        self.prompt_lines = []

    def __get_reply(self):
        data = ''
        ret = []
        while True:
            block = self.control_socket.recv(1024)
            data += block
            if data.endswith('\r\n'):
                data = data.split()


    def __send_msg(self, msg):
        self.control_socket.send(msg)


    def __set_PASV(self):
        msg = 'PASV\r\n'
        self.__send_msg(msg)
        self.prompt_lines += [msg]
        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '227':
            return 0
        # parse ip and port
        ans = self.prompt_lines[-1]
        ans = pasv_re.search(ans)
        if ans is None:
            return 0
        self.transmit_ip = ''
        for i in range(1, 4):
            self.transmit_ip += ans.group(i) + '.'
        self.transmit_ip += ans.group(4)
        self.transmit_port = int(ans.group(5)) * 256 + int(ans.group(6))
        return 1


    def __set_PORT(self):
        self.data_socket.bind('', 0)
        ip, port = self.data_socket.getsockname()
        ip.replace('.', ',', 3)
        port = ',%d,%d' % (port//256, port % 256)
        msg = 'PORT ' + ip + port + '\r\n'
        self.prompt_lines.append(msg)
        self.__send_msg(msg)
        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '227':
            return 0
        self.data_socket.listen(1)
        return 1


    def connect(self):
        # connect
        self.control_socket.connect((self.server_ip, self.server_port))
        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '230':
            return 0

        # login
        msg = 'USER ' + self.username + '\r\n'
        self.prompt_lines.append(msg)
        self.__send_msg(msg)
        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '331':
            return 0

        # password
        msg = 'PASS ' + self.password + '\r\n'
        self.prompt_lines.append(msg)
        self.__send_msg(msg)
        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '230':
            return 0

        # set binary mode
        msg = 'TYPE I\r\n'
        self.prompt_lines.append(msg)
        self.__send_msg(msg)
        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '200':
            return 0

        # now login succeed
        return 1


    def retrieve_file(self, filename):
        if self.mode == 'PASV':
            # set pasv mode
            if self.__set_PASV() == 0:
                return 0
        else:
            # set port mode
            if self.__set_PORT() == 0:
                return 0

        # send RETR
        msg = 'RETR ' + filename + '\r\n'
        self.prompt_lines.append(msg)
        self.__send_msg(msg)
        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '150':
            return 0
        if self.mode == 'PASV':
            # build connection
            self.data_socket.connect((self.transmit_ip, self.transmit_port))

        # receive data
        with open(os.path.join(self.local_directory, filename), 'wb') as f:
            f.write(data)
