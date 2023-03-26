#include "filelib.h"
#include "pico_hal.h"

void filesystem_init()
{
    if (pico_mount(true) != LFS_ERR_OK) {
        printf("Error mounting FS\n");
        exit(-1);
    }
}

void store(const char* file_name, const char* data)
{
    int file = pico_open(file_name, LFS_O_WRONLY | LFS_O_APPEND | LFS_O_CREAT);
    if (file < 0)
    {
        return;
    }
    pico_write(file, data, strlen(data));
    pico_close(file);
}

// Make sure to free this pointer or else memory leaks :)
bool retrieve(const char* file_name, char** str)
{
    int file = pico_open(file_name, LFS_O_RDONLY);
    if (file < 0)
    {
        return false;
    }
    struct lfs_info info;
    int res = pico_stat(file_name, &info);
    if (res < 0)
    {
        pico_close(file);
        return false;
    }
    size_t file_size = info.size;
    *str = (char *) malloc(file_size + 1);
    if (*str == NULL)
    {
        pico_close(file);
        return false;
    }

    ssize_t bytes_read = pico_read(file, *str, file_size);
    pico_close(file);

    if (bytes_read != file_size)
    {
        free(*str);
        return false;
    }

    (*str)[file_size] = '\0';
    return true;
}
