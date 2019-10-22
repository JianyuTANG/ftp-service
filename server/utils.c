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
    int sockfd, i, ret;
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
 
    bzero(&servaddr, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    inet_pton(AF_INET, "127.0.0.1", &servaddr.sin_addr);
    for(i = 20000;i < 65535;i++)
    {
        servaddr.sin_port = htons(i);
        ret = connect(sockfd, (struct sockaddr *)&servaddr, sizeof(servaddr));
        if(0 == ret)
        {
            close(sockfd);
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

void *receive_file(void *arg)
{
    threadArgs *args = (threadArgs *)arg;
    int filefd = args->filefd;
    Connection *c = args->c;
    int isPASV = args->isPASV;
    int fd = args->fd;
    char file_buf[BUFFER_SIZE];
    bzero(file_buf, BUFFER_SIZE);
    int block_len = 0;
    while(1)
    {
        if((block_len = read(c->transmit_fd, file_buf, BUFFER_SIZE)) < 0)
        {
            c->transmit_status = NONE;
            close(c->transmit_fd);
            close(filefd);
            emit_message(fd, "426 Connection broken!\r\n");
            return NULL;
        }
        else if(block_len == 0)
        {
            break;
        }
        write(filefd, file_buf, block_len);
        bzero(file_buf, BUFFER_SIZE);
    }
    close(filefd);

    // transmitting success
    c->transmit_status = NONE;
    close(c->transmit_fd);
    if(isPASV)
    {
        close(c->PASV_listen_fd);
    }
    emit_message(fd, "226 Transfer complete.\r\n");
    return NULL;
}


void *send_file(void *arg)
{
    threadArgs *args = (threadArgs *)arg;
    int filefd = args->filefd;
    Connection *c = args->c;
    int isPASV = args->isPASV;
    int fd = args->fd;
    char file_buf[BUFFER_SIZE];
    bzero(file_buf, BUFFER_SIZE);
    int block_len = 0;
    printf("start reading file\n");
    int counter = 0;
    while((block_len = read(filefd, file_buf, BUFFER_SIZE)) > 0)
    {
        // printf("block\n");
        counter += block_len;
        if(write(c->transmit_fd, file_buf, block_len) < 0)
        {
            c->transmit_status = NONE;
            close(c->transmit_fd);
            if(isPASV)
            {
                close(c->PASV_listen_fd);
            }
            emit_message(fd, "426 Connection broken!\r\n");
            return NULL;
        }
        bzero(file_buf, BUFFER_SIZE);
    }
    close(filefd);

    printf("transfered %d bytes\n", counter);
    
    // transmitting success
    emit_message(fd, "226 Transfer complete.\r\n");
    c->transmit_status = NONE;
    close(c->transmit_fd);
    if(isPASV)
    {
        close(c->PASV_listen_fd);
    }
    printf("finsih transmitting\n");
    return NULL;
}