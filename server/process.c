#include "server.h"

int process(int fd)
{
    // read message
    char buffer[DIRECTORY_SIZE];
    read(fd, buffer, DIRECTORY_SIZE);
}