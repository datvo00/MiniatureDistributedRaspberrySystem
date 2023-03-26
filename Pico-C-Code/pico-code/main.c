#include <stdio.h>
#include <stdlib.h>
#include "pico/stdlib.h"
#include "display.h"
#include "filelib.h"

int main()
{
    stdio_init_all();
    filesystem_init();
    display_init();
    display_write("Storing");
    store("test.txt", "AWIN CHEATED ");
    store("test.txt", "ON 342 MIDTERM");
    display_write("Retrieving");
    char* data;
    if (retrieve("test.txt", &data))
    {
        display_write(data);
        free(data);
    }
    display_write("Bye");
    return 0;
}
