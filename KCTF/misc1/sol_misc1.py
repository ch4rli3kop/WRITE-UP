from pwn import *

r = remote('ctf.kuality.kr',12345)

while True:
	content = str(r.recv(0x130,timeout=0.1))
	index = content.find('KCTF{')
	if index != -1 :
		print(content[index:])
		r.close()
		break

	r.send('1')

r.interactive()