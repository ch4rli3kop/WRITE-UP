# [pwnable.kr] leg writeup



##### [summary] arm, pipelining

```shell
Daddy told me I should study arm.
But I prefer to study my leg!

Download : http://pwnable.kr/bin/leg.c
Download : http://pwnable.kr/bin/leg.asm

ssh leg@pwnable.kr -p2222 (pw:guest)
```

arm 문제다. 접속하면 qemu로 접속하게 되는데, leg를 실행해주면 된다. 



```c
#include <stdio.h>
#include <fcntl.h>
int key1(){
	asm("mov r3, pc\n");
}
int key2(){
	asm(
	"push	{r6}\n"
	"add	r6, pc, $1\n"
	"bx	r6\n"
	".code   16\n"
	"mov	r3, pc\n"
	"add	r3, $0x4\n"
	"push	{r3}\n"
	"pop	{pc}\n"
	".code	32\n"
	"pop	{r6}\n"
	);
}
int key3(){
	asm("mov r3, lr\n");
}
int main(){
	int key=0;
	printf("Daddy has very strong arm! : ");
	scanf("%d", &key);
	if( (key1()+key2()+key3()) == key ){
		printf("Congratz!\n");
		int fd = open("flag", O_RDONLY);
		char buf[100];
		int r = read(fd, buf, 100);
		write(0, buf, r);
	}
	else{
		printf("I have strong leg :P\n");
	}
	return 0;
}
```

key1(), key2(), key3()의 리턴 값을 추측하여 10진수 정수로 입력해주면 플래그를 출력해주는 문제이다.

amd에서 함수의 리턴 값이 rax에 저장되는 것처럼, arm에서 함수의 리턴 값은 r0에 저장된다. 각각의 함수의 리턴 값을 조사해보자.

### key1

```asm
(gdb) disass key1
Dump of assembler code for function key1:
   0x00008cd4 <+0>:	push	{r11}		; (str r11, [sp, #-4]!)
   0x00008cd8 <+4>:	add	r11, sp, #0
   0x00008cdc <+8>:	mov	r3, pc
   0x00008ce0 <+12>:	mov	r0, r3
   0x00008ce4 <+16>:	sub	sp, r11, #0
   0x00008ce8 <+20>:	pop	{r11}		; (ldr r11, [sp], #4)
   0x00008cec <+24>:	bx	lr
End of assembler dump.
```

`mov r0, r3`를 봤을 때, r3에 저장된 값을 알아내면 리턴 값을 알아낼 수 있을 것이다. r3에 값이 저장되는 부분은 `mov r3, pc`인데, 얼필봐선 r3에 0x00008ce0이 저장될 것 같지만 실제로는 0x00008ce4가 저장된다. 이는 pipelining 때문인데, 다음 표를 보면 이해가 될 것이다.

| Fetch     | Decode    | Execute   |
| --------- | --------- | --------- |
| instruct1 |           |           |
| instruct2 | instruct1 |           |
| instruct3 | instruct2 | instruct1 |

Fetch는 '가져오다'라는 뜻을 가졌는데, 그 뜻과 같이 메모리에 존재하는 pc가 가리키는 명령 코드를 가져오는 역할을 한다. Decode는 해당 명령어를 해석하여 어떤 일을 수행하는지 또 어떤 레지스터가 사용되는지 알아본다. 마지막으로 Execute는 해당 명령어를 실행하는 단계이다.

따라서 위의 명령어의 경우를 살펴보자면, `mov r3, pc`가 Execute 단계에 접어들 때 `sub sp, r11, #0`이 Fetch 단계에 들어선다는 것이다. pipelining 시, pc는 항상 Fetch하는 곳을 가리키게 되므로 `mov r3, pc`가 실행 될 때, pc의 값은 0x00008ce4이다. 즉, key1()의 __리턴 값은 0x00008ce4이다.__

### key2

```asm
(gdb) disass key2
Dump of assembler code for function key2:
   0x00008cf0 <+0>:	push	{r11}		; (str r11, [sp, #-4]!)
   0x00008cf4 <+4>:	add	r11, sp, #0
   0x00008cf8 <+8>:	push	{r6}		; (str r6, [sp, #-4]!)
   0x00008cfc <+12>:	add	r6, pc, #1
   0x00008d00 <+16>:	bx	r6
   0x00008d04 <+20>:	mov	r3, pc
   0x00008d06 <+22>:	adds	r3, #4
   0x00008d08 <+24>:	push	{r3}
   0x00008d0a <+26>:	pop	{pc}
   0x00008d0c <+28>:	pop	{r6}		; (ldr r6, [sp], #4)
   0x00008d10 <+32>:	mov	r0, r3
   0x00008d14 <+36>:	sub	sp, r11, #0
   0x00008d18 <+40>:	pop	{r11}		; (ldr r11, [sp], #4)
   0x00008d1c <+44>:	bx	lr
End of assembler dump.
```

이 함수에서도 역시, 0x00008d04에서 pc 값을 r3에 저장되는데, pipelining 작업 때문에, pc가 0x00008d08을 가리킬 때, 0x00008d04가 실행되어 r3에는 0x00008d08이 저장될 것이다. 이 후에 r3에 4를 더한 뒤 r0에 저장하기 때문에, key2()의 __리턴 값은 0x00008d0c__이다.

### key3

```asm
(gdb) disass key3
Dump of assembler code for function key3:
   0x00008d20 <+0>:	push	{r11}		; (str r11, [sp, #-4]!)
   0x00008d24 <+4>:	add	r11, sp, #0
   0x00008d28 <+8>:	mov	r3, lr
   0x00008d2c <+12>:	mov	r0, r3
   0x00008d30 <+16>:	sub	sp, r11, #0
   0x00008d34 <+20>:	pop	{r11}		; (ldr r11, [sp], #4)
   0x00008d38 <+24>:	bx	lr
End of assembler dump.
```

lr은 서브 함수를 실행한 뒤, 원래 함수로 돌아오기 위해서 다음에 실행할 pc 값을 저장해 놓는 레지스터이다. main()에서 key3()를 호출한 뒤, 실행할 명령어의 주소가 저장되므로 0x00008d80가 r3에 저장되며, 최종적으로 key()은 __0x00008d80을 리턴한다.__

### main

```asm
(gdb) disass main
Dump of assembler code for function main:
   0x00008d3c <+0>:	push	{r4, r11, lr}
   0x00008d40 <+4>:	add	r11, sp, #8
   0x00008d44 <+8>:	sub	sp, sp, #12
   0x00008d48 <+12>:	mov	r3, #0
   0x00008d4c <+16>:	str	r3, [r11, #-16]
   0x00008d50 <+20>:	ldr	r0, [pc, #104]	; 0x8dc0 <main+132>
   0x00008d54 <+24>:	bl	0xfb6c <printf>
   0x00008d58 <+28>:	sub	r3, r11, #16
   0x00008d5c <+32>:	ldr	r0, [pc, #96]	; 0x8dc4 <main+136>
   0x00008d60 <+36>:	mov	r1, r3
   0x00008d64 <+40>:	bl	0xfbd8 <__isoc99_scanf>
   0x00008d68 <+44>:	bl	0x8cd4 <key1>
   0x00008d6c <+48>:	mov	r4, r0
   0x00008d70 <+52>:	bl	0x8cf0 <key2>
   0x00008d74 <+56>:	mov	r3, r0
   0x00008d78 <+60>:	add	r4, r4, r3
   0x00008d7c <+64>:	bl	0x8d20 <key3>
   0x00008d80 <+68>:	mov	r3, r0
   0x00008d84 <+72>:	add	r2, r4, r3
   0x00008d88 <+76>:	ldr	r3, [r11, #-16]
   0x00008d8c <+80>:	cmp	r2, r3
   0x00008d90 <+84>:	bne	0x8da8 <main+108>
   0x00008d94 <+88>:	ldr	r0, [pc, #44]	; 0x8dc8 <main+140>
   0x00008d98 <+92>:	bl	0x1050c <puts>
   0x00008d9c <+96>:	ldr	r0, [pc, #40]	; 0x8dcc <main+144>
   0x00008da0 <+100>:	bl	0xf89c <system>
   0x00008da4 <+104>:	b	0x8db0 <main+116>
   0x00008da8 <+108>:	ldr	r0, [pc, #32]	; 0x8dd0 <main+148>
   0x00008dac <+112>:	bl	0x1050c <puts>
   0x00008db0 <+116>:	mov	r3, #0
   0x00008db4 <+120>:	mov	r0, r3
   0x00008db8 <+124>:	sub	sp, r11, #8
   0x00008dbc <+128>:	pop	{r4, r11, pc}
   0x00008dc0 <+132>:	andeq	r10, r6, r12, lsl #9
   0x00008dc4 <+136>:	andeq	r10, r6, r12, lsr #9
   0x00008dc8 <+140>:			; <UNDEFINED> instruction: 0x0006a4b0
   0x00008dcc <+144>:			; <UNDEFINED> instruction: 0x0006a4bc
   0x00008dd0 <+148>:	andeq	r10, r6, r4, asr #9
End of assembler dump.
```



따라서, `0x00008ce4 + 0x00008d0c + 0x00008d80 = 108400` 가 되어 key 값으로 108400을 입력하면 플래그를 얻을 수 있다.

```shell
/ $ ./leg 
Daddy has very strong arm! : 108400
Congratz!
My daddy has a lot of ARMv5te muscle!
```

