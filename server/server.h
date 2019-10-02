#ifndef SERVER_H
#define SERVER_H

#include <sys/types.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/select.h>
#include <strings.h>

#define DIRECTORY_SIZE 200
#define BUFFER_SIZE 2048
#define NUM_COMMANDS 17

#define CONTROL_PORT 21

extern int server_port;
extern char root_path[DIRECTORY_SIZE];

extern char *commands[];

extern int (*ftp_func[NUM_COMMANDS])(int fd, char* buffer);

int USER_func(int fd, char* buffer);
int PASS_func(int fd, char* buffer);
int RETR_func(int fd, char* buffer);
int STOR_func(int fd, char* buffer);
int QUIT_func(int fd, char* buffer);
int SYST_func(int fd, char* buffer);
int TYPE_func(int fd, char* buffer);
int PORT_func(int fd, char* buffer);
int PASV_func(int fd, char* buffer);
int MKD_func(int fd, char* buffer);
int CWD_func(int fd, char* buffer);
int PWD_func(int fd, char* buffer);
int LIST_func(int fd, char* buffer);
int RMD_func(int fd, char* buffer);
int RNFR_func(int fd, char* buffer);
int RNTO_func(int fd, char* buffer);
int REST_func(int fd, char* buffer);

#endif