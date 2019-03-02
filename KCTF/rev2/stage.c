#include<stdio.h>
#include<stdlib.h>
#include<string.h>
void stage1();
void stage2();
void stage3();
void stage4();
void stage5(int z, int r, int m);


static int A = 0;
static int R = 0;
static int M = 0;

int main() {

	setvbuf(stdout, 0, 2, 0);
	setvbuf(stdin, 0, 2, 0);
	setvbuf(stderr, 0, 2, 0);

	stage4();
	stage1();
	stage2();
	stage3();
	stage4();
	stage5(A, R, M);

	system("pause");

	return 0;

}

void stage1() {

	int answer = 20181217;
	int num = 0;

	printf("Welcome!!\nThis is stage 1\n");
	printf("Input Number: ");
	scanf("%d", &num);

	if (num == answer) {
		printf("Next Stage!\n");
		A = 10;
	}
	else {
		printf("FAIL!!\n");
		exit(0);
	}
}

void stage2() {
	char ai[100] = { 0, };
	int asc[100] = { 0, };
	int cnt_ai = 0;
	int cnt_asc = 0;
	int i = 0;
	int r = 0;

	printf("Stage 2!!\n");
	printf("Input : ");
	scanf("%s", ai);
	cnt_ai = strlen(ai);


	for (i = 0; i < cnt_ai; i++) {
		printf("input: ");
		scanf("%d", &asc[i]);
	}

	for (i = 0; i<cnt_ai; i++) {
		if (asc[i] == ai[i]) {
			r++;
		}
		else
			r = 0;
	}

	if (r == cnt_ai) {
		printf("Next Stage!!\n");
		R = 10;
	}
	else {
		printf("FAIL!!\n");
		exit(0);
	}
}

void stage3() {

	int num=0;
	char al = 0;
	int input = 0;
	printf("Input: ");
	scanf("%d %d %c", &num, &input, &al);

	switch (num) {
	case 32:
		if (al == input - num) {
			printf("Next Stage!!\n");
			M = 5;
		}
		break;
	case 46:
		if (al == input - num) {
			printf("Next Stage!!\n");
			M = 6;
		}
		break;
	case 193:
		if (al == input - num) {
			printf("Next Stage!!\n");
			M = 7;
		}
		break;
	case 421:
		if (al == input - num) {
			printf("Next Stage!!\n");
			M = 8;
		}
		break;
	case 264:
		if (al == input - num) {
			printf("Next Stage!!\n");
			M = 9;
		}
		break;
	case 2234:
		if (al == input - num) {
			printf("Next Stage!!\n");
			M = 10;
		}
		break;
	default:
		printf("FAIL!!\n");
		exit(0);
	}
}

void stage4() {
	int a[777] = { 0, };
	int b = 0;

	int i = 0;
	printf("Input 777 times: ");
	
	 for (i = 0; i < 777; i++) {
      scanf("%d", &a[i]);
   }
	

	printf("Goood Job!!\n You can go next stage!!\n");

}

void stage5 (int z, int r, int m) {
	int i = 0;
	int a = 0;
	char ar1[11] = { "Fvqf8k0Njb>" };
	char ar2[11] = { "4fc]1f0PnkI" };
	char ar3[11] = { "Fuoc4f*GbY4" };
	
	char l1[11] = { 0, };
	char l2[11] = { 0, };
	char l3[11] = { 0, };
	
	printf("Here is flag stage!!\n");

	if (z + r + m > 24 && z + r + m < 31) {
		a = 3;
		for (i = 0; i < 11; i++) {
			l1[i] = ar2[i] - i + 19 - i * a;
		}
	}
	else if (A + R + M > 32 && A + R + M < 39) {
		a = 4;
		for (i = 0; i < 11; i++) {
			l2[i] = ar1[i] - i + 19 + i * a;
		}
	}
	else if (A + R + M > 39 && A + R + M < 41) {
		a = 5;
		for (i = 0; i < 11; i++) {
			l3[i] = ar3[i] - i + 19 + i * a;
		}
	}
	else
		exit(0);

	printf("Flag:");
	for (i = 0; i < 11; i++) {
		printf("%c", l1[i]);
	}
	printf("\n");
}

