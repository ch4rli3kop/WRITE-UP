from pwn import *

context.log_level = 'debug'

r = remote('pwnable.kr',9007)

r.recvuntil("- Ready? starting in 3 sec... -\n")
    
for k in range(100):    
    r.recvuntil("N=")
    num = int(r.recvuntil("C=").split(' ')[0])
    chance = int(r.recvline())

    start = 0
    end = num - 1
 
    for i in range(0, chance):
        mid = (start + end) // 2
        msg = ''
        for j in range(start, mid+1): msg += (str(j) + ' ')
        r.sendline(msg)
        res = int(r.recvline())
        if res%10 == 9:
            print([str(j) for j in range(start, mid+1)])
            end = mid
        else:
            print([str(j) for j in range(mid+1, end+1)])
            start = mid + 1
    
    r.sendline(str(start))
    r.recvline()

r.interactive()
