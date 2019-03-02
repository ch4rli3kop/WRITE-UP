from pwn import *
 
r = remote('ctf.kuality.kr',12348)

r.recvuntil('Then, Work hard!\n\n')

for i in range(0,100):	
	tmp = str(r.recvline()[:-5])
	answer = eval(tmp)
	r.sendlineafter('> ',str(answer))
	r.recvuntil('OK right answer!\n\n',timeout=0.1)

r.interactive()