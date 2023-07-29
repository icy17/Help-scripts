#include <stdio.h>
#include <stdlib.h>


void target(char* str)
{
    str[0] = 'i';
}

void right(void)
{
    char* str;
    
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
    target(str);
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
    
    target(str);
}

void wrong2_right(void)
{
    char* str;
    
    
    target(str);
    if(str == NULL)
    {
        str = malloc(10);
        // return;
    }
    free(str);
}

void wrong3(void)
{
    char* str;
    free(str);
}

int main(void){
    char* str;
    // str = malloc(10);
    free(str);
    // right();
    // wrong1();
    // wrong2_right();
}