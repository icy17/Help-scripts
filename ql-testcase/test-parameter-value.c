#include <stdio.h>

void target(char* str)
{
    str[0] = 'i';
}

void right(void)
{
    char* str;
    str = malloc(10);
    if(str == NULL)
    {
        return;
    }
    target(str);
}

void wrong1(void)
{
    char* str;
    if(str == NULL)
    {
        return;
    }
    str = malloc(10);
    
    target(str);
}

void wrong2(void)
{
    char* str;
    str = malloc(10);
    
    target(str);
}

int main(void){
    char* str;
    str = malloc(10);
    right();
    wrong1();
    wrong2();
}