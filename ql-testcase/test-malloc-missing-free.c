#include <stdio.h>
#include <stdlib.h>


void target(char* str)
{
    str[0] = 'i';
}

void new_malloc(char* str)
{
    str[0] = 'i';
}

void new_free(char* str)
{
    free(str);
}

void right(void)
{
    char* str;
    str = malloc(10);
    if(str == NULL)
    {
        free(str);
        return;
    }
    free(str);
    target(str);
}

void wrong1(void)
{
    char* str;
    int i = rand();
    str = malloc(10);
    if(i == 1)
    {
        return;
    }
    free(str);
    
    target(str);
}

void wrong2_right(void)
{
    char* str;
    str = malloc(10);
    
    target(str);
    if(str == NULL)
    {
        return;
    }
    free(str);
}

void wrong3(void)
{
    char* str;
    str = malloc(10);
}

void wrong4(void)
{
    char* str;
    str = malloc(10);
    if(str)
    {
        free(str);
    }
    
}

void right_new(void)
{
    char* str;
    new_malloc(str);
    free(str);
}

void wrong_new(void)
{
    char* str;
    new_malloc(str);
    // free(str);
}

void right_new2(void)
{
    char* str;
    new_malloc(str);
    new_free(str);
}



int main(void){
    char* str;
    str = malloc(10);
    right();
    wrong1();
    wrong2_right();
}