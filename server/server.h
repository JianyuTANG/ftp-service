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
#include <ctype.h>
#include <dirent.h>
#include <sys/select.h>
#include <fcntl.h>
#include <sys/ioctl.h> 
#include <unistd.h>
#include <string.h>

#define DIRECTORY_SIZE 200
#define BUFFER_SIZE 2048
#define NUM_COMMANDS 17
#define CONTROL_PORT 21
#define MAX_CLIENT_NUM 500

typedef enum TransmitStatus
{
    NONE,
    READY_PASV,
    READY_PORT,
    TRANSMITTING,
    START_RENAME
}transmitStatus;

typedef enum LoginStatus
{
    OUT,
    USERNAME_OK,
    LOGGED_IN
}loginStatus;

typedef struct Connection
{
    int fd;
    char current_directory[DIRECTORY_SIZE];
    char current_renaming_filename[DIRECTORY_SIZE];
    loginStatus login_status;
    transmitStatus transmit_status;
    int transmit_fd;
    int PASV_listen_fd;
    int transmit_port;
    char client_ip[100];
    int client_port;
} Connection;

extern int server_port;
extern char default_path[DIRECTORY_SIZE];
extern char my_ip[50];

int process(int fd);
int connection_process(int server_sockfd, fd_set *readfds);

extern char *commands[];
extern int (*ftp_func[NUM_COMMANDS])(int, char*);

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

extern Connection *connection[MAX_CLIENT_NUM];
void register_connection(int fd, Connection* p);
Connection* get_connection(int fd);
int get_available_port();
void get_my_ip();

int emit_message(int fd, char *msg);

int change_working_directory(char *tgt_directory, Connection *c);
int make_dir(char *dirname, char *current_directory);
int remove_dir(char *dirname, char *current_directory);
int is_file(char *filename, char *current_directory);
int rename_file(char *tgt_filename, char *src_filename, char *current_directory);
int join_path(char *source, char *target);

#endif