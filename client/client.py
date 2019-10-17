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
                ret += data.split('\r\n')
                ret = ret[:-1]
                data = ''
                if ret[-1][3] == ' ':
                    break
        return ret


    def __send_msg(self, msg):
        self.control_socket.sendall(msg)


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
        # build connection
        self.data_socket.connect((self.transmit_ip, self.transmit_port))
        return 1


    def __set_PORT(self):
        self.data_socket.bind('', 0)
        ip, port = self.data_socket.getsockname()
        ip.replace('.', ',', 3)
        port = ',%d,%d' % (port//256, port % 256)
        msg = 'PORT ' + ip + port
        self.prompt_lines.append(msg)
        self.__send_msg(msg + '\r\n')
        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '227':
            return 0
        self.data_socket.listen(1)
        return 1


    def __close_socket(self, flag):
        if flag == 0:
            self.control_socket.close()
            self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.data_socket.close()
            self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def connect(self):
        # connect
        self.control_socket.connect((self.server_ip, self.server_port))
        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '230':
            return 0

        # login
        msg = 'USER ' + self.username
        self.prompt_lines.append(msg)
        self.__send_msg(msg + '\r\n')
        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '331':
            return 0

        # password
        msg = 'PASS ' + self.password
        self.prompt_lines.append(msg)
        self.__send_msg(msg + '\r\n')
        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '230':
            return 0

        # set binary mode
        msg = 'TYPE I'
        self.prompt_lines.append(msg)
        self.__send_msg(msg + '\r\n')
        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '200':
            return 0

        # now login succeed
        self.connection_status = 'logged in'
        self.local_directory = os.getcwd()
        return 1


    def quit(self):
        msg = 'ABOR'
        self.prompt_lines.append(msg)
        self.__send_msg(msg + '\r\n')
        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '221':
            pass
        self.__close_socket(0)
        self.__close_socket(1)
        self.connection_status = 'None'


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
        msg = 'RETR ' + filename
        self.prompt_lines.append(msg)
        self.__send_msg(msg + '\r\n')
        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '150':
            return 0

        # accept data connection
        if self.mode == 'PORT':
            sock = self.data_socket
            self.data_socket = sock.accept()

        # receive and write data
        content = ''
        while True:
            block = self.data_socket.recv(1024)
            content += block
            if not block:
                break
        self.__close_socket(1)
        if self.mode == 'PORT':
            sock.close()
        try:
            f = open(os.path.join(self.local_directory, filename), 'wb')
            f.write(content)
            f.close()
        except:
            return 0

        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '226':
            return 0

        return 1


    def store_file(self, local_filename, server_filename):
        if self.mode == 'PASV':
            # set pasv mode
            if self.__set_PASV() == 0:
                return 0
        else:
            # set port mode
            if self.__set_PORT() == 0:
                return 0

        # read local file
        try:
            f = open(os.path.join(self.local_directory, local_filename), 'wb')
            content = f.read()
            f.close()
        except:
            return 0

        # send STOR
        msg = 'STOR ' + server_filename
        self.prompt_lines.append(msg)
        self.__send_msg(msg + '\r\n')
        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '150':
            return 0

        # accept data connection
        if self.mode == 'PORT':
            sock = self.data_socket
            self.data_socket = sock.accept()

        # send data
        len = len(content)
        for cursor in range(0, len, 1024):
            block = content[cursor:min(len, cursor + 1024)]
            self.data_socket.sendall(block)
        self.__close_socket(1)
        if self.mode == 'PORT':
            sock.close()

        # finish transmitting
        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '226':
            return 0

        return 1


    def make_dir(self, dirname):
        msg = 'MKD ' + dirname
        self.prompt_lines.append(msg)
        self.__send_msg(msg + '\r\n')
        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '250' or self.prompt_lines[-1][:3] != '257':
            return 0
        return 1


    def remove_dir(self, dirname):
        msg = 'RMD ' + dirname
        self.prompt_lines.append(msg)
        self.__send_msg(msg + '\r\n')
        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '250':
            return 0
        return 1


    def rename(self, src_filename, tgt_filename):
        msg = 'RNFR ' + src_filename
        self.prompt_lines.append(msg)
        self.__send_msg(msg + '\r\n')
        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '350':
            return 0
        msg = 'RNTO ' + src_filename
        self.prompt_lines.append(msg)
        self.__send_msg(msg + '\r\n')
        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '250':
            return 0
        return 1


    def list(self):
        if self.mode == 'PASV':
            # set pasv mode
            if self.__set_PASV() == 0:
                return 0
        else:
            # set port mode
            if self.__set_PORT() == 0:
                return 0

        # send LIST
        msg = 'LIST'
        self.prompt_lines.append(msg)
        self.__send_msg(msg + '\r\n')
        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '150':
            return 0

        # accept data connection
        if self.mode == 'PORT':
            sock = self.data_socket
            self.data_socket = sock.accept()

        # receive data
