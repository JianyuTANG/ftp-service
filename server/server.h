#ifndef SERVER_H
#define SERVER_H

#include <sys/types.h>
#include <sys/stat.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <stdio.h>
#include <fcntl.h>
#include <sys/select.h>
#include <strings.h>

#define DIRECTORY_SIZE 200
#define BUFFER_SIZE 2048

extern int server_port;
extern char root_path[DIRECTORY_SIZE];

#endif