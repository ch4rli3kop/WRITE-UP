# [pwnable.kr] input writeup



##### [summary] input method

```shell
Mom? how can I pass my input to a computer program?

ssh input2@pwnable.kr -p2222 (pw:guest)
```

여러가지 입력 방법에 대한 문제인듯하다.



```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>

int main(int argc, char* argv[], char* envp[]){
	printf("Welcome to pwnable.kr\n");
	printf("Let's see if you know how to give input to program\n");
	printf("Just give me correct inputs then you will get the flag :)\n");

	// argv
	if(argc != 100) return 0;
	if(strcmp(argv['A'],"\x00")) return 0;
	if(strcmp(argv['B'],"\x20\x0a\x0d")) return 0;
	printf("Stage 1 clear!\n");	

	// stdio
	char buf[4];
	read(0, buf, 4);
	if(memcmp(buf, "\x00\x0a\x00\xff", 4)) return 0;
	read(2, buf, 4);
        if(memcmp(buf, "\x00\x0a\x02\xff", 4)) return 0;
	printf("Stage 2 clear!\n");
	
	// env
	if(strcmp("\xca\xfe\xba\xbe", getenv("\xde\xad\xbe\xef"))) return 0;
	printf("Stage 3 clear!\n");

	// file
	FILE* fp = fopen("\x0a", "r");
	if(!fp) return 0;
	if( fread(buf, 4, 1, fp)!=1 ) return 0;
	if( memcmp(buf, "\x00\x00\x00\x00", 4) ) return 0;
	fclose(fp);
	printf("Stage 4 clear!\n");	

	// network
	int sd, cd;
	struct sockaddr_in saddr, caddr;
	sd = socket(AF_INET, SOCK_STREAM, 0);
	if(sd == -1){
		printf("socket error, tell admin\n");
		return 0;
	}
	saddr.sin_family = AF_INET;
	saddr.sin_addr.s_addr = INADDR_ANY;
	saddr.sin_port = htons( atoi(argv['C']) );
	if(bind(sd, (struct sockaddr*)&saddr, sizeof(saddr)) < 0){
		printf("bind error, use another port\n");
    		return 1;
	}
	listen(sd, 1);
	int c = sizeof(struct sockaddr_in);
	cd = accept(sd, (struct sockaddr *)&caddr, (socklen_t*)&c);
	if(cd < 0){
		printf("accept error, tell admin\n");
		return 0;
	}
	if( recv(cd, buf, 4, 0) != 4 ) return 0;
	if(memcmp(buf, "\xde\xad\xbe\xef", 4)) return 0;
	printf("Stage 5 clear!\n");

	// here's your flag
	system("/bin/cat flag");	
	return 0;
}
```

복잡해보이지만 단계 별로 공략해나가면 쉽다.



#### Stage 1

```c
// argv
if(argc != 100) return 0;
if(strcmp(argv['A'],"\x00")) return 0;
if(strcmp(argv['B'],"\x20\x0a\x0d")) return 0;
printf("Stage 1 clear!\n");	
```

argv[65], argv[66]과 argc가 100이 되도록 만든다. 문제는 0x20은 space를 나타내는데, argv 인자는 이를 기준으로 나뉜다. 이를 어떻게 입력으로 줘야할까 고민을 했는데, pwntools을 이용하면 쉽게 넘겨줄 수 있다.

```python
from pwn import *

context.log_level = 'debug'

argvs = ["" for i in range(100)]
argvs[0] = "./input"
argvs[65] = "\x00"
argvs[66] = "\x20\x0a\x0d"

r = process(argv=argvs)

r.interactive()
```



#### Stage 2

```c
// stdio
char buf[4];
read(0, buf, 4);
if(memcmp(buf, "\x00\x0a\x00\xff", 4)) return 0;
read(2, buf, 4);
    if(memcmp(buf, "\x00\x0a\x02\xff", 4)) return 0;
printf("Stage 2 clear!\n");
```

표준 입력과 표준 에러로 입력을 줄 수 있는지 묻는다. 표준 에러가 문제인데, 이는 표준 에러에 맞춰줄 파일 디스크립터를 생성하여 process 생성 시에, stderr로 넘겨줄 수 있다. 

```python
stderrfd = open('./stderr','w+')
stderrfd.write('\x00\x0a\x02\xff')
stderrfd.seek(0)

r = process(executable='./input',argv=argvs, stderr=stderrfd)
r.recvuntil('Stage 1 clear!\n')
r.send("\x00\x0a\x00\xff")
```

유의해야 할 점 : 파일에 쓰고 난 뒤, 현재 파일 포인터의 위치는 4가 된다. 따라서 읽기 위해서는 파일 포인터를 파일의 시작으로 바꿔줘야 한다.



#### Stage 3

```c
// env
if(strcmp("\xca\xfe\xba\xbe", getenv("\xde\xad\xbe\xef"))) return 0;
printf("Stage 3 clear!\n");
```

환경변수를 만들어줄 수 있는지를 묻는다. process 생성 시에 만든 환경변수를 쉽게 넘겨줄 수 있다.

```python
r = process(executable='./input',argv=argvs, stderr=stderrfd, env={'\xde\xad\xbe\xef':'\xca\xfe\xba\xbe'})
```



#### Stage 4

```c
// file
FILE* fp = fopen("\x0a", "r");
if(!fp) return 0;
if( fread(buf, 4, 1, fp)!=1 ) return 0;
if( memcmp(buf, "\x00\x00\x00\x00", 4) ) return 0;
fclose(fp);
printf("Stage 4 clear!\n");	
```

fread로 fp에서 4바이트짜리 1개를 읽어서 buf에 저장하게 된다. 파일을 생성해서 해당 값을 써주면 해결

```python
with open('./\x0a', 'w') as fd:
        fd.write('\x00\x00\x00\x00')
```



#### Stage 5

```c
// network
int sd, cd;
struct sockaddr_in saddr, caddr;
sd = socket(AF_INET, SOCK_STREAM, 0);
if(sd == -1){
    printf("socket error, tell admin\n");
    return 0;
}
saddr.sin_family = AF_INET;
saddr.sin_addr.s_addr = INADDR_ANY;
saddr.sin_port = htons( atoi(argv['C']) );
if(bind(sd, (struct sockaddr*)&saddr, sizeof(saddr)) < 0){
    printf("bind error, use another port\n");
        return 1;
}
listen(sd, 1);
int c = sizeof(struct sockaddr_in);
cd = accept(sd, (struct sockaddr *)&caddr, (socklen_t*)&c);
if(cd < 0){
    printf("accept error, tell admin\n");
    return 0;
}
if( recv(cd, buf, 4, 0) != 4 ) return 0;
if(memcmp(buf, "\xde\xad\xbe\xef", 4)) return 0;
printf("Stage 5 clear!\n");
```

복잡해보이지만, 결국 로컬 주소에 argv[67] 값을 포트로 하여 서버로서 동작한다는 것이다. 해당 포트로 접속하여 "\xde\xad\xbe\xef"를 전송하면 된다.

```python
argvs[67] = "66666"
...
p = remote('127.0.0.1', 66666)
p.send('\xde\xad\xbe\xef')
```



## payload

```python
from pwn import *

context.log_level = 'debug'

argvs = ["" for i in range(100)]
argvs[0] = "/home/input2/input"
argvs[65] = "\x00"
argvs[66] = "\x20\x0a\x0d"
argvs[67] = "66666"

stderrfd = open('./stderr','w+')
stderrfd.write('\x00\x0a\x02\xff')
stderrfd.seek(0)

with open('./\x0a', 'w') as fd:
	fd.write('\x00\x00\x00\x00')

r = process(executable='/home/input2/input',argv=argvs, stderr=stderrfd, env={'\xde\xad\xbe\xef':'\xca\xfe\xba\xbe'})
r.recvuntil('Stage 1 clear!\n')
r.send("\x00\x0a\x00\xff")
r.recvuntil('Stage 2 clear!\n')
r.recvuntil('Stage 3 clear!\n')
r.recvuntil('Stage 4 clear!\n')

p = remote('127.0.0.1', 66666)
p.send('\xde\xad\xbe\xef')
p.close()

r.interactive()
```



```shell
input2@ubuntu:/tmp/ch4rli3$ ln -s /home/input2/flag flag
input2@ubuntu:/tmp/ch4rli3$ python sol.py 
[+] Starting local process '/home/input2/input' argv=['/home/input2/input', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ' \n\r', '66666', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']  env={'\xde\xad\xbe\xef': '\xca\xfe\xba\xbe'} : Done
[DEBUG] Received 0x92 bytes:
    'Welcome to pwnable.kr\n'
    "Let's see if you know how to give input to program\n"
    'Just give me correct inputs then you will get the flag :)\n'
    'Stage 1 clear!\n'
[DEBUG] Sent 0x4 bytes:
    00000000  00 0a 00 ff                                         │····││
    00000004
[DEBUG] Received 0xf bytes:
    'Stage 2 clear!\n'
[DEBUG] Received 0xf bytes:
    'Stage 3 clear!\n'
[DEBUG] Received 0xf bytes:
    'Stage 4 clear!\n'
[+] Opening connection to 127.0.0.1 on port 66666: Done
[DEBUG] Sent 0x4 bytes:
    00000000  de ad be ef                                         │····││
    00000004
[*] Closed connection to 127.0.0.1 port 66666
[*] Switching to interactive mode
[DEBUG] Received 0xf bytes:
    'Stage 5 clear!\n'
Stage 5 clear!
[DEBUG] Received 0x37 bytes:
    'Mommy! I learned how to pass various input in Linux :)\n'
Mommy! I learned how to pass various input in Linux :)

```

flag에 대해 심볼릭 링크를 걸어준 뒤, 실행하면 완료

