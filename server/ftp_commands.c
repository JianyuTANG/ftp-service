#include "server.h"

char *commands[] = {
    "USER",
    "PASS",
    "RETR",
    "STOR",
    "QUIT",
    "SYST",
    "TYPE",
    "PORT",
    "PASV",
    "MKD",
    "CWD",
    "PWD",
    "LIST",
    "RMD",
    "RNFR",
    "RNTO",
    "REST",
};

ftp_func[NUM_COMMANDS] = {
    USER_func,
    PASS_func,
    RETR_func,
    STOR_func,
    QUIT_func,
    SYST_func,
    TYPE_func,
    PORT_func,
    PASV_func,
    MKD_func,
    CWD_func,
    PWD_func,
    LIST_func,
    RMD_func,
    RNFR_func,
    RNTO_func,
    REST_func,
};

int USER_func(int fd, char* buffer)
{
    Connection* c = get_connection(fd);
    if(c->login_status >= LOGGED_IN)
    {
        return emit_message(fd, "530 Already logged in!\r\n");
    }
    if(strcmp(buffer+5, "annonymous"))
    {
        return emit_message(fd, "500 Wrong username!\r\n");
    }
    c->login_status = USERNAME_OK;
    return emit_message(fd, "331 Guest login ok,send your complete e-mail address as password.\r\n");
}

int PASS_func(int fd, char* buffer)
{
    Connection* c = get_connection(fd);
    loginStatus s = c->login_status;
    if(s == OUT)
    {
        return emit_message(fd, "530 No username yet!\r\n");
    }
    else if(s == USERNAME_OK)
    {
        c->login_status = LOGGED_IN;
        return emit_message(fd, "230 Guest login ok, access restrictions apply.\r\n");
    }
    else if(s == LOGGED_IN)
    {
        return emit_message(fd, "530 Already logged in!\r\n");
    }
}

int SYST_func(int fd, char* buffer)
{
    return emit_message(fd, "215 UNIX Type:L8\r\n");
}

int TYPE_func(int fd, char* buffer)
{
    if(get_connection(fd)->login_status < LOGGED_IN)
    {
        return emit_message(fd, "530 Hasn't logged in yet.\r\n");
    }
    if(strcmp(buffer + 5, "I"))
    {
        return emit_message(fd, "500 Unknown command!\r\n");
    }
    return emit_message(fd, "200 Type set to I.\r\n");
}

int QUIT_func(int fd, char* buffer)
{
    emit_message(fd, "221 Goodbye.\r\n");
    return 0;
}

int ABOR_func(int fd, char* buffer)
{
    return QUIT_func(fd, buffer);
}

int PWD_func(int fd, char* buffer)
{
    Connection* c = get_connection(fd);
    if(c->login_status < LOGGED_IN)
    {
        return emit_message(fd, "530 Hasn't logged in yet.\r\n");
    }
    char ret_msg[DIRECTORY_SIZE];
    sprintf(ret_msg, "257 \"", c->current_directory, "\"\r\n");
    return emit_message(fd, ret_msg);
    /*
    char current_directory[DIRECTORY_SIZE];
    if(get_current_directory(current_directory))   // TODO change the func
    {
        char ret_msg[DIRECTORY_SIZE];
        sprintf(ret_msg, "257 \"", c->current_directory, "\"\r\n");
        return emit_message(fd, ret_msg);
    }
    return emit_message(fd, "550 Fail to print the directory.\r\n");
    */
}

int CWD_func(int fd, char* buffer)
{
    Connection* c = get_connection(fd);
    if(c->login_status < LOGGED_IN)
    {
        return emit_message(fd, "530 Hasn't logged in yet.\r\n");
    }
    if(change_working_directory(buffer + 4, c))
    {
        return emit_message(fd, "250 Okay.\r\n");
    }
    char ret_msg[DIRECTORY_SIZE];
    sprintf(ret_msg, "550 ", buffer + 4, " No such file or directory.\r\n");
    return emit_message(fd, ret_msg);
}

int MKD_func(int fd, char* buffer)
{
    Connection* c = get_connection(fd);
    if(c->login_status < LOGGED_IN)
    {
        return emit_message(fd, "530 Hasn't logged in yet.\r\n");
    }
    if(make_dir(buffer + 4, c->current_directory))
    {
        char ret_msg[DIRECTORY_SIZE];
        sprintf(ret_msg, "257 \"", buffer + 4, "\" created.\r\n");
        return emit_message(fd, ret_msg);
    }
    char ret_msg[DIRECTORY_SIZE];
    sprintf(ret_msg, "550 ", buffer + 4, " Fail to create the directory.\r\n");
    return emit_message(fd, ret_msg);
}

int RMD_func(int fd, char* buffer)
{
    Connection* c = get_connection(fd);
    if(c->login_status < LOGGED_IN)
    {
        return emit_message(fd, "530 Hasn't logged in yet.\r\n");
    }
    if(remove_dir(buffer + 4, c->current_directory))
    {
        char ret_msg[DIRECTORY_SIZE];
        sprintf(ret_msg, "250 \"", buffer + 4, "\" removed.\r\n");
        return emit_message(fd, ret_msg);
    }
    char ret_msg[DIRECTORY_SIZE];
    sprintf(ret_msg, "550 ", buffer + 4, " Fail to remove the directory.\r\n");
    return emit_message(fd, ret_msg);
}

int RNFR_func(int fd, char* buffer)
{
    Connection* c = get_connection(fd);
    if(c->login_status < LOGGED_IN)
    {
        return emit_message(fd, "530 Hasn't logged in yet.\r\n");
    }
    if(is_file(buffer + 4, c->current_directory))
    {
        c->transmit_status = START_RENAME;
        strcpy(c->current_renaming_filename, buffer + 4);
        char ret_msg[DIRECTORY_SIZE];
        sprintf(ret_msg, "350 \"", buffer + 4, "\" exists.\r\n");
        return emit_message(fd, ret_msg);
    }
    char ret_msg[DIRECTORY_SIZE];
    sprintf(ret_msg, "550 \"", buffer + 4, "\" doesn't exist.\r\n");
    return emit_message(fd, ret_msg);
}

int RNTO_func(int fd, char* buffer)
{
    Connection* c = get_connection(fd);
    if(c->login_status < LOGGED_IN)
    {
        return emit_message(fd, "530 Hasn't logged in yet.\r\n");
    }
    if(c->transmit_status != START_RENAME)
    {
        return emit_message(fd, "530 Hasn't started renaming yet.\r\n");
    }
    c->transmit_status = NONE;
    if(rename_file(buffer + 4, c->current_renaming_filename, c->current_directory))
    {
        return emit_message(fd, "250 Renamed successfully.\r\n");
    }
    return emit_message(fd, "550 Fail to rename.\r\n");
}

int LIST_func(int fd, char* buffer)
{
    Connection* c = get_connection(fd);
    if(c->login_status < LOGGED_IN)
    {
        return emit_message(fd, "530 Hasn't logged in yet.\r\n");
    }

    // ensure connection established
    if(c->transmit_status == READY_PASV)
    {
        ;
    }
    else if(c->transmit_status == READY_PORT)
    {
        c->transmit_fd = socket(AF_INET, SOCK_STREAM, 0);
        if(c->transmit_fd < 0)
        {
            return emit_message(fd, "425 Data connection not available!\r\n");
        }
        struct sockaddr_in client_addr;
        client_addr.sin_family = AF_INET;
        client_addr.sin_port = htons(c->client_port);
        client_addr.sin_addr.s_addr = inet_addr(c->client_ip);
        if(connect(clientSocket, (struct sockaddr *)&client_addr, sizeof(client_addr)) < 0)
        {
            return emit_message(fd, "425 Data connection not available!\r\n");
        }
    }
    else
    {
        return emit_message(fd, "425 Data connection not available!\r\n");
    }
}

int PORT_func(int fd, char* buffer)
{
    Connection* c = get_connection(fd);
    if(c->login_status < LOGGED_IN)
    {
        return emit_message(fd, "530 Hasn't logged in yet.\r\n");
    }

    // close existed connection
    if(c->transmit_status == READY_PASV)
    {
        close(c->transmit_fd);
    }

    // resolve parameters
    if(buffer[4] != ' ')
    {
        // Need parameters
        return emit_message(fd, "500 Unknown command!\r\n");
    }
    int cursor = 5;
    // get ip address
    strcpy(c->client_ip, "");
    for(int i = 0; i < 4; i++)
    {
        int p = 0;
        while(*(buffer + cursor + p) != ',' && *(buffer + cursor + p) != '\0')
        {
            p++;
        }
        if(*(buffer + cursor + p) == ',')
        {
            *(buffer + cursor + p) = '\0';
            sprintf(c->client_ip, c->client_ip, buffer + cursor);
            cursor += p + 1;
        }
        else
        {
            // Wrong format
            return emit_message(fd, "500 Unknown command!\r\n");
        }
        if(i < 3)
        {
            sprintf(c->client_ip, c->client_ip, ".");
        }
    }
    // get port
    int port = 0;
    for(int i = 0; i < 2; i++)
    {
        int p = 0;
        while(*(buffer + cursor + p) != ',' && *(buffer + cursor + p) != '\0')
        {
            p++;
        }
        if(i == 0 && *(buffer + cursor + p) == ',')
        {
            *(buffer + cursor + p) = '\0';
            port += atoi(buffer + cursor) * 256;
            cursor += p + 1;
        }
        else if(i == 1 && *(buffer + cursor + p) == '\0')
        {
            port += atoi(buffer + cursor);
            cursor += p + 1;
        }
        else
        {
            // Wrong format
            return emit_message(fd, "500 Unknown command!\r\n");
        }
    }
    c->client_port = port;
    c->transmit_status = READY_PORT;
    return emit_message(fd, "200 Port accepted!\r\n");
}

int PASV_func(int fd, char* buffer)
{
    Connection* c = get_connection(fd);
    if(c->login_status < LOGGED_IN)
    {
        return emit_message(fd, "530 Hasn't logged in yet.\r\n");
    }
    if(buffer[4] == ' ')
    {
        // No parameters are allowed for PASV.
        return emit_message(fd, "500 Unknown command!\r\n");
    }

    // close existed connection
    if(c->transmit_status == READY_PASV)
    {
        close(c->transmit_fd);
    }

    // establish new connection
    // build socket
    int server_sockfd;
    struct sockaddr_in server_addr;
    server_sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if(server_sockfd < 0)
    {
        return emit_message(fd, "550 Fail to build socket!");
    }
    // bind port
    bzero(&server_addr, sizeof(server_addr));
	server_addr.sin_family = AF_INET;
    //int port = get_available_port();
	server_addr.sin_port = htons(0);  // OS will allocate a port automatically
	server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    if(bind(serverSocket, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
    {
        return emit_message(fd, "550 Fail to build socket!");
    }
    if (listen(server_sockfd, 10) < 0)
	{
		return emit_message(fd, "550 Fail to build socket!");
	}

    //update status
    int port = (int)(ntohs(server_addr.sin_port));
    c->transmit_status = READY_PASV;
    c->transmit_port = port;
    c->PASV_listen_fd = server_sockfd;

    char ret_msg[DIRECTORY_SIZE];
    char h[4][10];
    for(int i=0; i < 4; i++)
    {
        itoa(h[i], my_ip[i], 10);
    }
    char p[2][10];
    itoa(p[0], port / 256, 10);
    itoa(p[1], port % 256, 10);
    sprintf(ret_msg, "227 =", h[0], ",", h[1], ",", h[2], ",", h[3], ",", p[0], ",", p[1]);
    return emit_message(fd, ret_msg);
}

int RETR_func(int fd, char* buffer)
{
    Connection* c = get_connection(fd);
    if(c->login_status < LOGGED_IN)
    {
        return emit_message(fd, "530 Hasn't logged in yet.\r\n");
    }

    // check parameter
    if(buffer[4] != ' ')
    {
        // Need parameters
        return emit_message(fd, "500 Unknown command!\r\n");
    }

    // check the file for transmitting
    char tgt_file[DIRECTORY_SIZE];
    strcpy(tgt_file, c->current_directory);
    if(join_path(tgt_file, buffer + 5) == 0)
    {
        return emit_message(fd, "550 File does not exist!\r\n");
    }


    // ensure connection established
    if(!emit_message(fd, "150 Opening binary data connection."))
    {
        return 0;
    }
    transmitStatus transmit_status = c->transmit_status;
    c->transmit_status = TRANSMITTING;
    int isPASV = 0;
    if(transmit_status == READY_PASV)
    {
        isPASV = 1;
        c->transmit_fd = accept(c->PASV_listen_fd, NULL, NULL);
        if(c->transmit_fd < 0)
        {
            c->transmit_status = NONE;
            close(c->transmit_fd);
            close(c->PASV_listen_fd);
            return emit_message(fd, "425 Data connection not available!\r\n");
        }
    }
    else if(transmit_status == READY_PORT)
    {
        c->transmit_fd = socket(AF_INET, SOCK_STREAM, 0);
        if(c->transmit_fd < 0)
        {
            c->transmit_status = NONE;
            close(c->transmit_fd);
            return emit_message(fd, "425 Data connection not available!\r\n");
        }
        struct sockaddr_in client_addr;
        client_addr.sin_family = AF_INET;
        client_addr.sin_port = htons(c->client_port);
        client_addr.sin_addr.s_addr = inet_addr(c->client_ip);
        if(connect(clientSocket, (struct sockaddr *)&client_addr, sizeof(client_addr)) < 0)
        {
            c->transmit_status = NONE;
            close(c->transmit_fd);
            return emit_message(fd, "425 Data connection not available!\r\n");
        }
    }
    else
    {
        return emit_message(fd, "425 Data connection not available!\r\n");
    }

    // start transmitting data

    // read and send the file
    int filefd = open(tgt_file, O_RDONLY);
    if(filefd < 0)
    {
        c->transmit_status = NONE;
        close(c->transmit_fd);
        return emit_message(fd, "451 Fail to read the file!\r\n");
    }
    char file_buf[BUFFER_SIZE];
    bzero(file_buf, BUFFER_SIZE);
    int block_len = 0;
    while((block_len = read(filefd, buffer, BUFFER_SIZE)) > 0)
    {
        if(send(c->transmit_fd, file_buf, block_len, 0) < 0)
        {
            c->transmit_status = NONE;
            close(c->transmit_fd);
            return emit_message(fd, "426 Connection broken!\r\n");
        }
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
    return emit_message(fd, "226 Transfer complete.\r\n");
}

int STOR_func(int fd, char* buffer)
{
    Connection* c = get_connection(fd);
    if(c->login_status < LOGGED_IN)
    {
        return emit_message(fd, "530 Hasn't logged in yet.\r\n");
    }

    // check parameter
    if(buffer[4] != ' ')
    {
        // Need parameters
        return emit_message(fd, "500 Unknown command!\r\n");
    }

    // check the file
    char tgt_file[DIRECTORY_SIZE];
    strcpy(tgt_file, c->current_directory);
    if(join_path(tgt_file, buffer + 5) == 0)
    {
        return emit_message(fd, "550 Can not create the file!\r\n");
    }
    int filefd = open(tgt_file, O_WRONLY | O_CREAT, S_IRWXU | S_IRWXG | S_IRWXO);
    if(filefd < 0)
    {
        return emit_message(fd, "452 Can not create the file!\r\n");
    }

    // ensure connection established
    if(!emit_message(fd, "150 Opening binary data connection."))
    {
        return 0;
    }
    transmitStatus transmit_status = c->transmit_status;
    c->transmit_status = TRANSMITTING;
    int isPASV = 0;
    if(transmit_status == READY_PASV)
    {
        isPASV = 1;
        c->transmit_fd = accept(c->PASV_listen_fd, NULL, NULL);
        if(c->transmit_fd < 0)
        {
            c->transmit_status = NONE;
            close(c->transmit_fd);
            close(c->PASV_listen_fd);
            return emit_message(fd, "425 Data connection not available!\r\n");
        }
    }
    else if(transmit_status == READY_PORT)
    {
        c->transmit_fd = socket(AF_INET, SOCK_STREAM, 0);
        if(c->transmit_fd < 0)
        {
            c->transmit_status = NONE;
            close(c->transmit_fd);
            return emit_message(fd, "425 Data connection not available!\r\n");
        }
        struct sockaddr_in client_addr;
        client_addr.sin_family = AF_INET;
        client_addr.sin_port = htons(c->client_port);
        client_addr.sin_addr.s_addr = inet_addr(c->client_ip);
        if(connect(clientSocket, (struct sockaddr *)&client_addr, sizeof(client_addr)) < 0)
        {
            c->transmit_status = NONE;
            close(c->transmit_fd);
            return emit_message(fd, "425 Data connection not available!\r\n");
        }
    }
    else
    {
        return emit_message(fd, "425 Data connection not available!\r\n");
    }

    // start transmitting data

    // read the file from TCP buffer
    char file_buf[BUFFER_SIZE];
    bzero(file_buf, BUFFER_SIZE);
    int block_len = 0;
    while(1)
    {
        if((block_len = read(c->transmit_fd, buffer, BUFFER_SIZE)) < 0)
        {
            c->transmit_status = NONE;
            close(c->transmit_fd);
            return emit_message(fd, "426 Connection broken!\r\n");
        }
        else if(block_len == 0)
        {
            break;
        }
        write(filefd, buffer, block_len);
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
    return emit_message(fd, "226 Transfer complete.\r\n");
}