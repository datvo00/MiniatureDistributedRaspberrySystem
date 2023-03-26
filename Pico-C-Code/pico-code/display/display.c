#include "display.h"
#include "OLED_2in23.h"
#include "GUI_Paint.h"
#include "stdlib.h"

UBYTE *BlackImage;

void display_init()
{
    DEV_Delay_ms(20);
    printf("OELD_test Demo\r\n");
    if(DEV_Module_Init()!=0)
    {
        while(1){
            printf("END\r\n");
        }
    }
    OLED_2in23_Init();
    UWORD Imagesize = ((OLED_2in23_WIDTH%8==0)? (OLED_2in23_WIDTH/8): (OLED_2in23_WIDTH/8+1)) * OLED_2in23_HEIGHT;
    if((BlackImage = (UBYTE *)malloc(Imagesize)) == NULL)
    {
        while(1){
            printf("Failed to apply for black memory...\r\n");
        }
    }
    Paint_NewImage(BlackImage, OLED_2in23_WIDTH, OLED_2in23_HEIGHT, 0, BLACK);
    Paint_SelectImage(BlackImage);
}

void display_write(const char* str)
{
    DEV_Delay_ms(1500);
    Paint_Clear(BLACK);
    Paint_DrawString_EN(10, 0, str, &Font12, WHITE, BLACK);
    OLED_2in23_draw_bitmap(0,0,&BlackImage[0],128,32);
}