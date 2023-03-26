aux_source_directory(. DIR_FILE_SRCS)

include_directories(../littlefs-lib)

add_library(file ${DIR_FILE_SRCS})
target_link_libraries(file littlefs-lib)