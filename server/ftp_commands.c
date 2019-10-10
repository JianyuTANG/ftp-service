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
    char current_directory[DIRECTORY_SIZE];
    if(get_current_directory(current_directory))   // TODO change the func
    {
        char ret_msg[DIRECTORY_SIZE];
        sprintf(ret_msg, "257 \"", c->current_directory, "\"\r\n");
        return emit_message(fd, ret_msg);
    }
    return emit_message(fd, "550 Fail to print the directory.\r\n");
}

int CWD_func(int fd, char* buffer)
{
    Connection* c = get_connection(fd);
    if(c->login_status < LOGGED_IN)
    {
        return emit_message(fd, "530 Hasn't logged in yet.\r\n");
    }
    if(change_working_directory(buffer + 4, c->current_directory))
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
    if(is_file(buffer + 4))
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
    if(rename_file(buffer + 4, c->current_renaming_filename))
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

}

int PORT_func(int fd, char* buffer)
{
    Connection* c = get_connection(fd);
    if(c->login_status < LOGGED_IN)
    {
        return emit_message(fd, "530 Hasn't logged in yet.\r\n");
    }
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
    c->transmit_status = READY_PASV;
    
    // build socket
    int server_sockfd;
    struct sockaddr_in server_addr;
    server_sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if(server_sockfd < 0)
    {
        printf("ERROR: Fail to build socket.\n");
        return 0;
    }
    // bind port
    bzero(&server_addr, sizeof(server_addr));
	server_addr.sin_family = AF_INET;
    int port = get_available_port();
	server_addr.sin_port = htons(port);
	server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    if(bind(serverSocket, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
    {
        printf("ERROR: Fail to bind the port 21.\n");
        return 0;
    }
    if (listen(server_sockfd, 10) < 0)
	{
		printf("Error listen(): %s(%d)\n", strerror(errno), errno);
		return 0;
	}

    char ret_msg[DIRECTORY_SIZE];
    char h[4][10];
    for(int i=0; i < 4; i++)
    {
        itoa(h[i], my_ip[i], 10);
    }
    char p[2][10];
    itoa(p[0], port / 256, 10);
    itoa(p[1], port % 256, 10);
    sprintf(ret_msg, "227 =", h[0], h[1], h[2], h[3], p[0], p[1]);
    return emit_message(fd, ret_msg);
}

int RETR_func(int fd, char* buffer)
{
}

int STOR_func(int fd, char* buffer)
{

}