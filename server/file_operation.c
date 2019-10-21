#include "server.h"


int change_working_directory(char *buffer, Connection *c)
{
    DIR *dp;
    dp = opendir(c->current_directory);
    if(dp == NULL)
    {
        return 0;
    }
    closedir(dp);

    // change to current dir
    chdir(c->current_directory);
    dp = opendir(buffer);
    // check the availabilty of the target dir
    if(dp == NULL)
    {
        return 0;
    }
    closedir(dp);
    join_path(c->current_directory, buffer);
    return 1;
}

int make_dir(char *dirname, char *current_directory)
{
    char current_dir[DIRECTORY_SIZE];
    strcpy(current_dir, current_directory);
    if(join_path(current_dir, dirname) == 0)
    {
        return 0;
    }
    if(mkdir(current_dir, 0777))
    {
        return 0;
    }
    return 1;
}

int rm_dir(char *dirname)
{
    DIR *dp;
	struct dirent *entry;
	struct stat dstat;
    char *up = "..";
    char *current = ".";

    dp = opendir(dirname);
    if(dp == NULL)
    {
        // cannot open the dir
        return 0;
    }

    chdir(dirname);
    while((entry = readdir(dp)) != NULL)
    {
        stat(entry->d_name, &dstat);
        if(S_ISDIR(dstat.st_mode))
        {
            if(!strcmp(entry->d_name, up) || !strcmp(entry->d_name, current))
            {
                continue;
            }
            rm_dir(entry->d_name);
        }
        else if(S_ISREG(dstat.st_mode))
        {
            remove(entry->d_name);
        }
        else
        {
            return 0;
        }
        
    }
    closedir(dp);
    chdir(up);
    rmdir(dirname);
    return 1;
}

int remove_dir(char *dirname, char *current_directory)
{
    char current_dir[DIRECTORY_SIZE];
    strcpy(current_dir, current_directory);
    if(join_path(current_dir, dirname) == 0)
    {
        return 0;
    }
    return rm_dir(current_dir);
}

int is_file(char *filename, char *current_directory)
{
    char current_dir[DIRECTORY_SIZE];
    strcpy(current_dir, current_directory);
    if(join_path(current_dir, filename) == 0)
    {
        return 0;
    }
    if(access(current_dir, F_OK))
    {
        return 0;
    }
    struct stat dstat;
    if(stat(current_dir, &dstat) < 0)
    {
        return 0;
    }
    if(S_ISREG(dstat.st_mode) || S_ISDIR(dstat.st_mode))
    {
        return 1;
    }
    return 0;
}

int rename_file(char *tgt_filename, char *src_filename, char *current_directory)
{
    char src[DIRECTORY_SIZE], tgt[DIRECTORY_SIZE];
    strcpy(src, current_directory);
    join_path(src, src_filename);
    strcpy(tgt, current_directory);
    join_path(tgt, tgt_filename);
    if(!rename(src, tgt))
    {
        return 1;
    }
    return 0;
}

int join_path(char *source, char *target)
{
    if(target[0] == '/')
    {
        // absolute path
        strcpy(source, target);
    }
    else
    {
        // relative path

        // divide current_dir
        int depth = 0;
        int pos[100];
        pos[0] = 1;
        char current_dir[DIRECTORY_SIZE];
        strcpy(current_dir, source);
        int cursor = 1;
        while(current_dir[cursor] != '\0')
        {
            if(current_dir[cursor] == '/')
            {
                depth++;
                current_dir[cursor] = '\0';
                pos[depth] = cursor + 1;
            }
            cursor++;
        }
        if(current_dir[1] != '\0')
        {
            depth++;
        }

        // divide target_dir
        char target_dir[DIRECTORY_SIZE];
        strcpy(target_dir, target);
        int tdepth = 1;
        int tpos[100];
        tpos[0] = 0;
        cursor = 0;
        while(target_dir[cursor] != '\0')
        {
            if(target_dir[cursor] == '/')
            {
                target_dir[cursor] = '\0';
                tpos[depth] = cursor + 1;
                tdepth++;
            }
            cursor++;
        }

        // join them
        char *up = "..";
        char *current = ".";
        int divide = depth;
        for(int i = 0; i < tdepth; i++)
        {
            if(!strcmp(target_dir + tpos[i], up))
            {
                // go to the upper directory
                depth--;
                if(depth < 0)
                {
                    return 0;
                }
                if(depth < divide)
                {
                    divide = depth;
                }
            }
            else if(!strcmp(target_dir + tpos[i], current))
            {
                // stay current
                // do nothing
                ;
            }
            else
            {
                pos[depth] = tpos[i];
                depth++;
            }
        }
        strcpy(source, "/");
        for(int i = 0; i < divide; i++)
        {
            if( i != depth - 1)
            {
                sprintf(source, "%s%s/", source, current_dir + pos[i]);
            }
            else
            {
                sprintf(source, "%s%s", source, current_dir + pos[i]);
            }
        }
        for(int i = divide; i < depth; i++)
        {
            if( i != depth - 1)
            {
                sprintf(source, "%s%s/", source, target_dir + pos[i]);
            }
            else
            {
                sprintf(source, "%s%s", source, target_dir + pos[i]);
            }
        }
    }
    return 1;
}