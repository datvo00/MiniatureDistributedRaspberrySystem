# 查找当前目录下的所有源文件
# 并将名称保存到 DIR_examples_SRCS 变量
aux_source_directory(. DIR_display_SRCS)

include_directories(../screenlib/Config)
include_directories(../screenlib/GUI)
include_directories(../screenlib/Icm20948)
include_directories(../screenlib/OLED)
include_directories(../screenlib/Fonts)

# 生成链接库
add_library(display ${DIR_display_SRCS})
target_link_libraries(display PUBLIC Config OLED Icm20948 GUI Fonts)