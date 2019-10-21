#include "server.h"

Connection *connection[MAX_CLIENT_NUM] = {NULL};

int process(int fd)
{
    // read the command
    char buffer[DIRECTORY_SIZE];
    int len = read(fd, buffer, DIRECTORY_SIZE);

    // resolve command
    if(len < 2)
    {
        // devoid of \r\n
        return 0;
    }
    
    if(buffer[len - 1] == '\n' && buffer[len - 2] == '\r')
    {
        // end with \r\n
        buffer[len - 2] = '\0';
        printf("%s\n", buffer);
        char *mid = strchr(buffer, (int)' ');
        if(mid)
        {
            int n = mid - buffer;
            if(n >= 5)
            {
                // command longer than 4 letters
                return 0;
            }

            // legal command
            // extract command
            char command[5];    
            for(int i = 0; i < n; i++)
            {
                command[i] = toupper(buffer[i]);
            }
            command[n] = '\0';

            // find correspondent function to call
            for(int i = 0; i < NUM_COMMANDS; i++)
            {
                if(!strcmp(command, commands[i]))
                {
                    // call
                    int result = (*ftp_func[i])(fd, buffer);
                    return result;
                }
            }
        }
        else
        {
            char command[5];
            int n = len - 2;
            if(n >= 5)
            {
                // command longer than 4 letters
                return 0;
            }
            for(int i = 0; i < n; i++)
            {
                command[i] = toupper(buffer[i]);
            }
            command[n] = '\0';
            for(int i = 0; i < NUM_COMMANDS; i++)
            {
                if(!strcmp(command, commands[i]))
                {
                    // call
                    int result = (*ftp_func[i])(fd, buffer);
                    // printf("6666\n");
                    return result;
                }
            }
            return 0;
        }    
    }
    return 0;
}


int connection_process(int server_sockfd, fd_set *readfds)
{
    //unsigned int client_len = sizeof(client_addr);
    printf("start processing\n");
    int client_sockfd = accept(server_sockfd, 0, 0);
    printf("%d\n", client_sockfd);
    FD_SET(client_sockfd, readfds);
    Connection* c = (Connection*)malloc(sizeof(Connection));
    c->fd = client_sockfd;
    strcpy(c->current_directory, default_path);
    c->login_status = OUT; // unlogged
    register_connection(client_sockfd, c);
    return emit_message(client_sockfd, "220 FTP server ready.\r\n");
}