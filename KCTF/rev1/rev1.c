#include<stdio.h>

char str1[0x10] = "KCTF";
char str2[0x10] = "{V3Ry_v3R";
char str3[0x10] = "Y_S133py...}";

int main(){

	char str[0x30] = "";

	printf("%s%s%s",str1,str2,str3);

	return 0;
}