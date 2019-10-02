#include "server.h"

int size = 0;

void register_connection(int fd, Connection* p)
{
    if(size >= MAX_CLIENT_NUM)
    {
        return;
    }
    connection[size] = p;
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