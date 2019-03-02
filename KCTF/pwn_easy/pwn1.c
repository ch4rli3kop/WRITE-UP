#include<stdio.h>

/*simple bof problem*/

int initialize(){
	setvbuf(stdout, 0, 2, 0);
	setvbuf(stdin, 0, 2, 0);
	setvbuf(stderr, 0, 2, 0);
	return 0;
}

void getshell(){

	system("/bin/sh");
}

struct str{
	char str[256];
	int check;	
};

int main(){
	
	struct str a;
	

	initialize();
	a.check = 0xbeefdead;
	printf("get shell for this?\n");
	printf("> ");
	read(0,a.str,0x1000);

	if(a.check == 0xdeadbeef)
		getshell();
	else
		puts(a.str);

	return 0;
}
