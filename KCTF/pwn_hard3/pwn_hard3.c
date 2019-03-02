#include<stdio.h>
#include<stdlib.h>

char glo[0x1000] = "";
char glo2[0x1000] = "";
char glo3[0x1000] = "";
char glo4[0x1000] = "";


int initialize(){
	//chdir("/home/pwn5");
	setvbuf(stdout, 0, 2, 0);
	setvbuf(stdin, 0, 2, 0);
	setvbuf(stderr, 0, 2, 0);
	return 0;
}

void getinp(char * ptr, int size){
	int length;

	length = read(0, ptr, size);

	if(length == -1)
		exit(0);
	if(ptr[length] == 0x0a)
		ptr[length] = '\x00';
}

int main(){

	char str[0x40];

	initialize();

	printf("AAAA : ");
	getinp(glo4, 0x1000);
	printf("BBBB : ");
	getinp(str,0x50);

	return 0;
}