#include "server.h"

int size = 0;
Connection *connection[MAX_CLIENT_NUM];

void register_connection(int fd, Connection* p)
{
    if(size >= MAX_CLIENT_NUM)
    {
        return;
    }
    connection[size] = p;
    size++;
}

Connection* get_connection(int fd)
{
    for(int i = 0; i < size; i++)
    {
        if(connection[i])
        {
            if(connection[i]->fd == fd)
            {
                return connection[i];
            }
        }
    }
    return 0;
}

int emit_message(int fd, char *msg)
{
    int result = 0;
    result = write(fd, msg, strlen(msg));
    if(result < 0)
    {
        return 0;
    }
    return 1;
}

int get_available_port()
{
    struct sockaddr_in servaddr;
    int sockfd, i, serverport, ret;
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
 
    bzero(&servaddr, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    inet_pton(AF_INET, "127.0.0.1", &servaddr.sin_addr);
    for(i = 20000;i < 65535;i++)
    {
        servaddr.sin_port = htons(i);
        ret = connect(sockfd, (struct sockaddr *)&servaddr, sizeof(servaddr));
        if(EISCONN == ret)
        {
            close(sockfd)
        }
      else
        {
            return i;
        } 
    }
    return 0;
}

void get_my_ip()
{
    int listenfd = socket(AF_INET, SOCK_DGRAM, 0);
	struct sockaddr_in addr;
	memset(&addr, 0, sizeof(addr));
	addr.sin_family = AF_INET;
	addr.sin_port = htons(80);
	addr.sin_addr.s_addr = htonl(INADDR_ANY);
	inet_pton(AF_INET, "8.8.8.8", &(addr.sin_addr.s_addr));
	connect(listenfd, (struct sockaddr *)&(addr), sizeof(addr));

	socklen_t n = sizeof addr;
	getsockname(listenfd, (struct sockaddr *)&addr, &n);
	inet_ntop(AF_INET, &(addr.sin_addr), my_ip, INET_ADDRSTRLEN);
}