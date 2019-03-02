#include<stdio.h>
#include<stdlib.h>
#include<time.h>
#include<string.h>
#include<math.h>

int choice = 0;

int initialize(){
	setvbuf(stdout, 0, 2, 0);
	setvbuf(stdin, 0, 2, 0);
	setvbuf(stderr, 0, 2, 0);
	alarm(10);
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

void filtering(char* ptr){
	int i, len;
	char str[0x30] = "";
	len = strlen(ptr);
	for(i=0;i<len;i++){
		if(ptr[i] == ';' || ptr[i] == '|' || ptr[i] == '&' || ptr[i] == ')'){
			ptr[i] = '\x00';
		}
	}

	printf("you select : ");
	sprintf(str,"echo %s",ptr);
	system(str);
}



int getint(){
	char ptr[0x20];

	memset(ptr,0,0x20);
	getinp(ptr,0x20);

	filtering(ptr);

	return atoi(ptr);
}


void menu(){
	puts("1. rock");
	puts("2. paper");
	puts("3. scissors");
	printf("> ");
	choice = getint();
}


void case1(){

	battle((choice+1)%3, choice );
	puts("Congratulation!");
	puts("You Win!");
	system("cat flag.txt");
	exit(0);
}

void battle(int user, int com){

	puts("====== You =======");
	switch(user){
		case 0:
			puts("    _______");
			puts("---'   ____)");
			puts("      (_____)");
			puts("      (_____)");
			puts("      (____)");
			puts("---.__(___)");
			puts("");
			break;
		case 1:
			puts("    _______");
			puts("---'   ____)____");
			puts("          ______)");
			puts("          _______)");
			puts("         _______)");
			puts("---.__________)");
			puts("");
			break;
		case 2:
			puts("    _______");
			puts("---'   ____)____");
			puts("          ______)");
			puts("       __________)");
			puts("      (____)");
			puts("---.__(___)");
			puts("");
	}


	puts("==== Computer ====");
	switch(com){
		case 0:
			puts("    _______");
			puts("---'   ____)");
			puts("      (_____)");
			puts("      (_____)");
			puts("      (____)");
			puts("---.__(___)");
			puts("");
			break;
		case 1:
			puts("    _______");
			puts("---'   ____)____");
			puts("          ______)");
			puts("          _______)");
			puts("         _______)");
			puts("---.__________)");
			puts("");
			break;
		case 2:
			puts("    _______");
			puts("---'   ____)____");
			puts("          ______)");
			puts("       __________)");
			puts("      (____)");
			puts("---.__(___)");
			puts("");
	}

}

void case2(){

	int i = rand()%2;

	battle(choice, (choice+i)%3);
	if(i)
		puts("Sorry... You Lose!...");
	else
		puts("That's too bad!");
	puts("...haha...try again!\n\n");
}


void main(){

	initialize();
	srand(time(NULL));
	int random = 0;
	
	while(1){

		do{
			menu();
		}while(!(1<=choice && choice <= 3));

		choice -= 1;
		random = rand()%7777;
		
		switch(random){
			case 7:
				case1();
				break;
			default:
				case2();
		}
	}

}
