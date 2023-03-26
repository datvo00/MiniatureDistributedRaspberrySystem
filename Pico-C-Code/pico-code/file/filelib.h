#ifndef _FILELIB_H
#define _FILELIB_H

#include <stdbool.h>

void filesystem_init();
void store(const char* file_name, const char* data);
bool retrieve(const char* file_name, char** str);

#endif