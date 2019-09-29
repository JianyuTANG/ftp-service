#include "server.h"

int main(int argc, char **argv)
{
    if(argc != 1 && argc != 5 && argc != 3)
    {
        // only 1 3 5 arguments are accepted
        printf("ERROR: Wrong number of arguments!\n")
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
            strcpy(root_path, argv[2]);
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
                strcpy(root_path, argv[4]);
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
                strcpy(root_path, argv[2]);
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
        strcpy(root_path, "/tmp");
    }
    
    
    return 0;
}