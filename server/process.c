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
            for{int i = 0; i < NUM_COMMANDS; i++}
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
            return 0;
        }
        
    }
    return 0;
}
