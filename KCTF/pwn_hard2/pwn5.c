#include<stdio.h>
#include<string.h>
#include<stdlib.h>

char glo1[0x1000] = "";
char glo2[0x1000] = "";
char glo3[0x1000] = "";
char glo4[0x1000] = "";
char comment_space[0x100] = "";

int initialize();
void getinp(char * ptr, int size);
int getint();
int printchoice();
void menu();

struct glo{
	int orders[0x10];
	int v1[0x10];
	int ordernum;
	int commentnum;
	int remain;
};

struct glo setup;


void ment(int price){
	printf("\n it's price is %d\n",price);

	puts(" pay the price after you finish your meal");
	printf(" order number : %d\n",setup.ordernum+1);

	setup.ordernum ++;
}

void order(char* str){

	if(!(1<=setup.remain&&setup.remain<=0x10)){
		puts(" Sorry! No table!");
		return;
	}
	setup.remain--;

	if(setup.ordernum > 0x10){
		puts(" Sorry! Food ingredients are exhausted!");
		return;
	}


	menu();
	getinp(str,0x10);

	if(!strcmp(str,"Gogi mandu")){
		setup.orders[setup.ordernum] = 500;
		ment(setup.orders[setup.ordernum]);
	}
	else if(!strcmp(str,"Kimchi mandu")){
		setup.orders[setup.ordernum] = 450;
		ment(setup.orders[setup.ordernum]);
	}
	else if(!strcmp(str,"Gamja mandu")){
		setup.orders[setup.ordernum] = 550;
		ment(setup.orders[setup.ordernum]);
	}
	else if(!strcmp(str,"Mul mandu")){
		setup.orders[setup.ordernum] = 400;
		ment(setup.orders[setup.ordernum]);
	}
	else if(!strcmp(str,"Gun mandu")){
		setup.orders[setup.ordernum] = 600;
		ment(setup.orders[setup.ordernum]);
	}
	else{
		puts(" Sorry that menu is not here!");
	}	
}

void payment(){

	int num;
	int pay;
	
	do{
		puts("");
		puts(" input order number");
		printf(" >> ");
		num = getint();
	}while(!setup.orders[num]);

	puts(" Give me the money");
	printf(" >> ");
	pay = getint();

	setup.orders[num] = pay - setup.orders[num];
}

void comment(){

	puts("");
	puts(" Please leave comment about the menu");
	printf(" >> ");
	getinp(comment_space,setup.commentnum);

}

struct mainspace{
	int choice;
	int choice1[3];
	char str[0x100];
};

int main(){

	struct mainspace a;

	initialize();


	while(1){
		printchoice();
		a.choice = getint();

		switch(a.choice){
			case 1:
			order(&(a.str[setup.ordernum*0x10]));
			break;
			case 2:
			payment();
			break;
			case 3:
			comment();
			break;
			case 4:
			puts(" bye! bye~!");
			return 0;
			default:
			printf(" invalid value");
			break;
		}
	}	
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


int printchoice(){

	puts("");
	puts(" ┏─────━ SELECT ━──────┓");
	puts(" │ 1. Order            │");  
	puts(" │ 2. Payment          │");
	puts(" │ 3. Leave a comment  │");
	puts(" │ 4. Exit             │");
	puts(" ┗━───────────────────━┛");
	printf(" >> ");

	return 0;
}


void menu(){

	puts("");
	puts("  ┏━━━━━━ MENU ━━━━━━┓");
	puts("  ┃ ◈  Gogi mandu    ┃");
	puts("  ┃ ◈  Kimchi mandu  ┃");
	puts("  ┃ ◈  Gamja mandu   ┃");
	puts("  ┃ ◈  Mul mandu     ┃");
	puts("  ┃ ◈  Gun mandu     ┃");
	puts("  ┗━━━━━━━━━━━━━━━━━━┛\n");
	puts(" Please typing your menu");
	printf(" >> ");

}

int initialize(){
	setvbuf(stdout, 0, 2, 0);
	setvbuf(stdin, 0, 2, 0);
	setvbuf(stderr, 0, 2, 0);


	setup.remain = 0x10;
	setup.commentnum = 0x10;

	puts("");
	puts("  !! Welcome to The Mandu Heaven !!");
	puts(" I hope that you have good meal here!");
	puts(" Please order now and pay when you leave.");

	return 0;
}