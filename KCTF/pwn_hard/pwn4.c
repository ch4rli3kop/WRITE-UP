#include<stdio.h>
#include<string.h>
#include<stdlib.h>

unsigned int size = 0;
char name[0x10] = "";

int initialize(){
	setvbuf(stdout, 0, 2, 0);
	setvbuf(stdin, 0, 2, 0);
	setvbuf(stderr, 0, 2, 0);

	puts("");
	puts("   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓");
	puts("   ┃            K  C  T  F             ┃");
	puts("   ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫");
	puts("   ┃                                   ┃");
	puts("   ┃        Welcome to our CTF!!       ┃");
	puts("   ┃                                   ┃");
	puts("   ┃  Please fill out the guest list!  ┃");
	puts("   ┃                                   ┃");
	puts("   ┃                        - Kuaity   ┃");
	puts("   ┃                                   ┃");
	puts("   ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫");
	puts("   ┃ Name : ch4rli3kop                 ┃");
	puts("   ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫");	
	puts("   ┃ Comment : Good Luck!              ┃");
	puts("   ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n");
	return 0;
}

void getinp(char * ptr, int size){
	int length;

	length = read(0, ptr, size);

	if(length == -1)
		exit(0);
	if(ptr[length-1] == 0x0a)
		ptr[length-1] = '\x00';
}

int getint(){
	char ptr[0x20];

	memset(ptr,0,0x20);
	getinp(ptr,0x20);
	
	return atoi(ptr);
}


int input_data(char * str){

	char str1[0x30];
	unsigned int size = 0;
	char buf[8];

	puts("");
	printf("   Input length : ");
	size = getint();

	printf("   Input comment : ");
	if((int)size <= 0x30){
		getinp(str1, size);
		strcpy(str,str1);
	}
	else{
		getinp(str1,0x30);
		strcpy(str,str1);
	}
	return strlen(str);
}

int printmenu(){

	printf("\n   ======== MENU ========\n");
	printf("   1.  Input comment\n");
	printf("   2.  View name\n");
	printf("   3.  View commment\n");
	printf("   4.  Exit\n");
	printf("   >> ");

	return 0;
}

void input_name(){
	puts("   Please enter visitor name");
	printf("   >> ");
	getinp(name,0x10);
}


void print_name(char* str){
	snprintf(str,0x30,name);
}

void view_name(){
	char str[0x30];
	print_name(str);
	printf("\n   Name : %s",str);
}

void view_data(char* str){
	char str1[0x30];
	strncpy(str1,str,0x30);
	printf("\n   Comment : %s",str1);
}


int main(){

	char str[0x30];
	int choice = 0;
	int size = 0;

	initialize();
	memset(str,0,0x30);

	input_name();

	while(1){
		printmenu();
		choice = getint();

		switch(choice){
			case 1:
				input_data(str);
				break;
			case 2:
				view_name();
				break;
			case 3:
				view_data(str);
				break;
			case 4:
				return 0;
			default:
				printf("invalid value");
				break;
		}
	}	
	return 0;
}
