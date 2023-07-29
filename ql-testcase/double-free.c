#include <stdio.h>
#include <stdlib.h>


void target(char* str)
{
    str[0] = 'i';
}

void initialize_api(char* str)
{
    str[0] = 'i';
}

void right(void)
{
    char* str;
    // strlen(str)
    if(str == NULL)
    {
        str = malloc(10);
        // return;
    }
    else
    {
        str = malloc(10);
    }
    free(str);
    
    // target(str);
}

void wrong1(void)
{
    char* str;
    int i = rand();
    
    if(i == 1)
    {
        str = malloc(10);
        // return;
    }
    free(str);
    if(i == 1)
    {
        free(str);
        // return;
    }
    
    // target(str);
}

void wrong2(void)
{
    char* str;
    int i = rand();
    
    if(i == 1)
    {
        str = malloc(10);
        // return;
    }
    free(str);
    if(i == 1)
    {
        target(str);
        // return;
    }
    
    
}

void wrong3(void)
{
    char* str;
    target(str);
    free(str);
}

void right2(void)
{
    char* str;
    free(str);
    str = malloc(1);
    free(str);
}

void right3(void)
{
    char* str;
    free(str);
    initialize_api(str);
    free(str);
}

int main(void){
    char* str;
    // str = malloc(10);
    free(str);
    free(str);
    // right();
    // wrong1();
    // wrong2_right();
}