#include "server.h"


char default_path[DIRECTORY_SIZE] = "/tmp";
int server_port = 21;
char my_ip[50];

int main(int argc, char **argv)
{
    get_my_ip();

    // process arugments
    if(argc != 1 && argc != 5 && argc != 3)
    {
        // only 1 3 5 arguments are accepted
        printf("ERROR: Wrong number of arguments!\n");
        return 0;
    }

    if(argc == 3)
    {
        if(!strcmp(argv[1], "-port"))
        {
            server_port = atoi(argv[2]);
        }
        else if(!strcmp(argv[1], "-root"))
        {
            strcpy(default_path, argv[2]);
        }
        else
        {
            printf("ERROR: Unknown argument!\n");
            return 0;
        }
        
    }
    else if(argc == 5)
    {
        if(!strcmp(argv[1], "-port"))
        {
            if(!strcmp(argv[3], "-root"))
            {
                server_port = atoi(argv[2]);
                strcpy(default_path, argv[4]);
            }
            else
            {
                printf("ERROR: Unknown argument!\n");
                return 0;
            }
        }
        else if(!strcmp(argv[1], "-root"))
        {
            if(!strcmp(argv[3], "-port"))
            {
                server_port = atoi(argv[4]);
                strcpy(default_path, argv[2]);
            }
            else
            {
                printf("ERROR: Unknown argument!\n");
                return 0;
            }
        }
    }
    else
    {
        server_port = 21;
        strcpy(default_path, "/tmp");
    }
    
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
	server_addr.sin_port = htons(server_port);
	server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    if(bind(server_sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
    {
        printf("ERROR: Fail to bind the port 21.\n");
        return 0;
    }

    // listen
    if (listen(server_sockfd, 10) < 0)
	{
		//printf("Error listen(): %s(%d)\n", strerror(errno), errno);
		return 0;
	}

    fd_set readfds, testfds;
    FD_ZERO(&readfds); 
	FD_SET(server_sockfd, &readfds);
    int client_sockfd;
    struct sockaddr_in client_addr;
    while(1)
    {
        int fd, nread;
        testfds = readfds;
        int result = select(FD_SETSIZE, &testfds, (fd_set *)0, (fd_set *)0, (struct timeval *) 0); 
		if(result < 1) 
		{ 
			perror("server5"); 
			exit(1); 
		}
        
        for(fd = 0; fd < FD_SETSIZE; fd++)
        {
            if(!FD_ISSET(fd, &testfds))
            {
                continue;
            }

            if(fd == server_sockfd)
            {
                unsigned int client_len = sizeof(client_addr); 
                client_sockfd = accept(server_sockfd, (struct sockaddr *) &client_addr, &client_len);
                FD_SET(client_sockfd, &readfds);
                Connection* c = (Connection*)malloc(sizeof(Connection));
                c->fd = client_sockfd;
                strcpy(c->current_directory, default_path);
                c->login_status = 0; // unlogged
                register_connection(client_sockfd, c);
            }
            else
            {
                ioctl(fd, FIONREAD, &nread);
                // process
                if(nread == 0)
				{
					close(fd);
					FD_CLR(fd, &readfds);
					printf("removing client on fd %d/n", fd);
                    continue;
				}
                process(fd);
            }
            
        }
    }

    return 0;
}
