#include<stdio.h>
#include<stdlib.h>
#include<string.h>

int initialize(){
	setvbuf(stdout, 0, 2, 0);
	setvbuf(stdin, 0, 2, 0);
	setvbuf(stderr, 0, 2, 0);
	return 0;
}

void view(){

	puts("\nCan you read this flag? ;b");
	puts("");
	puts("     .-.");
    puts("    (   )");
	puts("     |~|       _.--._  ");
	puts("     | |~:'--~'      | ");
	puts("     | | : system    | ");
	puts("     |~| :    /bin   | ");
	puts("     | | :      /sh  | ");
	puts("     | | :     _.--._| ");
	puts("     |~|~`'--~'        ");
	puts("     | |");
    puts("     | |");
    puts("     | |");
    puts("     | |");
    puts("     | |");
    puts("     | |");
    puts("     | |");
	puts("     | |");
	puts("     | |");  
	puts("_____|_|_________");
	puts("------------------------------------------------");
	puts("-------------------------------------------------------");
	puts("pwn2$ ls -l ./flag.txt");
	system("ls -l ./flag.txt");
	puts("-------------------------------------------------------");
	puts("\nCan you cat flag.txt  ;)");
}

void getinput(char * ptr, int size){
	int length;

	length = read(0, ptr, size);

	if(length == -1)
		exit(0);
	if(ptr[length-1] == 0x0a)
		ptr[length-1] = '\x00';
}

struct str{
	char str1[0x100];
	char str2[0x100];
	int check;
};

int main(){
	
	struct str a;
	
	initialize();
	memset(a.str1,0,0x100);
	memset(a.str2,0,0x100);
	a.check = 0xbeefdead;

	view();
	puts("");

	printf("Input data : ");
	getinput(a.str1,0x300);

	if (a.check == 0xdeadbeef)
		memcpy(a.str2,a.str1,0x250);
	else{
		strcpy(a.str1,a.str2);
		exit(0);
	}

	
	printf("OK 계획대로 되고있어");

	return 0;
}