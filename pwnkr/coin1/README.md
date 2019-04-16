# [pwnable.kr] coin1 writeup



##### [summary] binary search

```shell
Mommy, I wanna play a game!
(if your network response time is too slow, try nc 0 9007 inside pwnable.kr server)

Running at : nc pwnable.kr 9007
```

접속하면 다음과 같은 게임을 진행할 수 있다.



```shell

	---------------------------------------------------
	-              Shall we play a game?              -
	---------------------------------------------------
	
	You have given some gold coins in your hand
	however, there is one counterfeit coin among them
	counterfeit coin looks exactly same as real coin
	however, its weight is different from real one
	real coin weighs 10, counterfeit coin weighes 9
	help me to find the counterfeit coin with a scale
	if you find 100 counterfeit coins, you will get reward :)
	FYI, you have 60 seconds.
	
	- How to play - 
	1. you get a number of coins (N) and number of chances (C)
	2. then you specify a set of index numbers of coins to be weighed
	3. you get the weight information
	4. 2~3 repeats C time, then you give the answer
	
	- Example -
	[Server] N=4 C=2 	# find counterfeit among 4 coins with 2 trial
	[Client] 0 1 		# weigh first and second coin
	[Server] 20			# scale result : 20
	[Client] 3			# weigh fourth coin
	[Server] 10			# scale result : 10
	[Client] 2 			# counterfeit coin is third!
	[Server] Correct!

	- Ready? starting in 3 sec... -
	
N=606 C=10

```

[0, 1, 2... N-1] 내에서 단 하나의 위조 동전을 찾아야한다. 기회는 C번이다.

알고리즘 문제인데, binary search를 이용하면 쉽게 풀 수 있다.
$$
N <= 2^C
$$
 가 만족하도록 N과 C를 주기 때문에 binary search를 이용하면 무적권 찾을 수 있다.



```python
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
```



```shell
...
	'Correct! (99)\n'
[*] Switching to interactive mode
[DEBUG] Received 0x37 bytes:
    'Congrats! get your flag\n'
    'b1NaRy_S34rch1nG_1s_3asy_p3asy\n'
Congrats! get your flag
b1NaRy_S34rch1nG_1s_3asy_p3asy
```

