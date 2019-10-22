import os
import socket
import re


pasv_re = re.compile(r'(\d*),(\d*),(\d*),(\d*),(\d*),(\d*)')
pwd_re = re.compile('\"(.*)\"')


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
        self.server_file_list = []
        self.prompt_lines = []

    def __get_reply(self):
        data = ''
        ret = []
        while True:
            block = self.control_socket.recv(1024).decode()
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
        self.__send_msg(msg.encode())
        self.prompt_lines += [msg]
        self.prompt_lines += self.__get_reply()
        print(self.prompt_lines[-1])
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
        self.transmit_ip = self.server_ip
        self.transmit_port = int(ans.group(5)) * 256 + int(ans.group(6))
        # build connection
        try:
            self.data_socket.connect((self.transmit_ip, self.transmit_port))
        except:
            return 0
        return 1


    def __set_PORT(self):
        self.data_socket.bind(('', 0))
        self.data_socket.listen(1)
        ip, port = self.data_socket.getsockname()
        ip = ip.replace('.', ',')
        ip = '127,0,0,1'
        port = ',%d,%d' % (port//256, port % 256)
        msg = 'PORT ' + ip + port
        print(msg)
        self.prompt_lines.append(msg)
        self.__send_msg((msg + '\r\n').encode())
        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '200':
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
        try:
            self.control_socket.connect((self.server_ip, self.server_port))
        except:
            print('fail to connect')
            return 0
        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '220':
            return 0

        # login
        print('good')
        msg = 'USER ' + self.username
        self.prompt_lines.append(msg)
        self.__send_msg((msg + '\r\n').encode())
        self.prompt_lines += self.__get_reply()
        print(self.prompt_lines[-1])
        if self.prompt_lines[-1][:3] != '331':
            print('good')
            return 0

        # password
        print('good')
        msg = 'PASS ' + self.password
        self.prompt_lines.append(msg)
        self.__send_msg((msg + '\r\n').encode())
        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '230':
            return 0

        # set binary mode
        msg = 'TYPE I'
        self.prompt_lines.append(msg)
        self.__send_msg((msg + '\r\n').encode())
        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '200':
            return 0

        # now login succeed
        self.connection_status = 'logged in'
        self.local_directory = os.getcwd()
        print('good')
        return 1


    def quit(self):
        msg = 'QUIT'
        self.prompt_lines.append(msg)
        self.__send_msg((msg + '\r\n').encode())
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
        print('start RETR')
        msg = 'RETR ' + filename
        self.prompt_lines.append(msg)
        self.__send_msg((msg + '\r\n').encode())
        print('send')
        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '150':
            return 0
        print(self.prompt_lines[-1])

        # accept data connection
        sock = None
        if self.mode == 'PORT':
            sock = self.data_socket
            self.data_socket, addr = sock.accept()
        print(self.data_socket)

        # receive data and write
        try:
            f = open(os.path.join(self.local_directory, filename), 'wb')
        except:
            return 0
        while True:
            try:
                block = self.data_socket.recv(1024)
            except:
                print('fail')
                f.close()
                return 0
            if len(block) <= 0:
                break
            try:
                f.write(block)
            except:
                f.close()
                return 0
        self.__close_socket(1)
        if self.mode == 'PORT':
            sock.close()
        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '226':
            return 0
        print(self.prompt_lines[-1])

        f.close()
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
            f = open(os.path.join(self.local_directory, local_filename), 'rb')
            content = f.read()
            f.close()
        except:
            return 0

        # send STOR
        msg = 'STOR ' + server_filename
        self.prompt_lines.append(msg)
        self.__send_msg((msg + '\r\n').encode())
        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '150':
            return 0

        # accept data connection
        sock = None
        if self.mode == 'PORT':
            sock = self.data_socket
            self.data_socket, addr = sock.accept()

        # send data
        self.data_socket.sendall(content)
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
        self.__send_msg((msg + '\r\n').encode())
        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '250' and self.prompt_lines[-1][:3] != '257':
            return 0
        return 1


    def remove_dir(self, dirname):
        msg = 'RMD ' + dirname
        self.prompt_lines.append(msg)
        self.__send_msg((msg + '\r\n').encode())
        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '250':
            return 0
        return 1


    def rename(self, src_filename, tgt_filename):
        msg = 'RNFR ' + src_filename
        self.prompt_lines.append(msg)
        self.__send_msg((msg + '\r\n').encode())
        self.prompt_lines += self.__get_reply()
        print(self.prompt_lines[-1])
        if self.prompt_lines[-1][:3] != '350':
            return 0

        msg = 'RNTO ' + tgt_filename
        self.prompt_lines.append(msg)
        self.__send_msg((msg + '\r\n').encode())
        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '250':
            return 0
        return 1


    def list_server(self):
        print('real start')
        if self.mode == 'PASV':
            # set pasv mode
            if self.__set_PASV() == 0:
                return 0
        else:
            # set port mode
            if self.__set_PORT() == 0:
                return 0
        print('mode finish')

        # send LIST
        msg = 'LIST'
        self.prompt_lines.append(msg)
        self.__send_msg((msg + '\r\n').encode())
        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '150':
            return 0
        print(self.prompt_lines[-1])

        # accept data connection
        sock = None
        if self.mode == 'PORT':
            sock = self.data_socket
            self.data_socket, addr = sock.accept()
        print('accepted')
        print(self.data_socket)


        # receive data
        data = ''
        while True:
            try:
                block = self.data_socket.recv(1024).decode()
            except:
                print('fail')
            print('1')
            data += block
            if len(block) <= 0:
                break
        print(data)
        self.__close_socket(1)
        if self.mode == 'PORT':
            sock.close()
        self.prompt_lines += self.__get_reply()
        if self.prompt_lines[-1][:3] != '226':
            return 0
        print(self.prompt_lines[-1])

        print('finish transmitting')


        # parse data
        self.server_file_list.clear()
        print(data.splitlines())
        data = data.splitlines()[1:]

        for f in data:
            print(f)
            self.server_file_list.append(f.split(' ')[-1])
        print(self.server_file_list)

        return 1


    def get_server_directory(self):
        msg = 'PWD'
        self.prompt_lines.append(msg)
        self.__send_msg((msg + '\r\n').encode())
        self.prompt_lines += self.__get_reply()
        ans = self.prompt_lines[-1]
        if ans[:3] != '257':
            return 0
        self.server_directory = self.prompt_lines[-1].split(' ')[1][:-2]
        d = pwd_re.search(ans)
        if d is None:
            return 0
        self.server_directory = d.group(1)
        return 1


    def change_dir(self, tgt_dir):
        msg = 'CWD ' + tgt_dir
        self.prompt_lines.append(msg)
        self.__send_msg((msg + '\r\n').encode())
        self.prompt_lines += self.__get_reply()
        ans = self.prompt_lines[-1]
        if ans[:3] != '250':
            return 0
        return 1
