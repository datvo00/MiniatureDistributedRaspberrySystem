cmake_minimum_required(VERSION 3.12)
include(pico_sdk_import.cmake)
project(Pico_ePaper_Code)
pico_sdk_init()

add_subdirectory(screenlib/Config)
add_subdirectory(screenlib/OLED)
add_subdirectory(screenlib/Icm20948)
add_subdirectory(screenlib/Fonts)
add_subdirectory(screenlib/GUI)
add_subdirectory(examples)
add_subdirectory(display)
add_subdirectory(littlefs-lib)
add_subdirectory(file)

include_directories(FreeRTOS)
include_directories(examples)
include_directories(screenlib/Config)
include_directories(screenlib/GUI)
include_directories(screenlib/Icm20948)
include_directories(screenlib/OLED)
include_directories(display)
include_directories(littlefs-lib)
include_directories(file)

add_executable(main
        main.c
)

# enable usb output, disable uart output
pico_enable_stdio_usb(main 1)
pico_enable_stdio_uart(main 1)

# create map/bin/hex/uf2 file etc.
pico_add_extra_outputs(main)
target_link_libraries(main pico_stdlib hardware_spi Config Fonts
        GUI Icm20948 OLED examples display littlefs-lib file)

