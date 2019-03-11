# bandit

심심해서 다시 시작해봤다.

### bandit0 -> bandit1

```shell
> cat readme
boJ9jbbUNNfktd78OOpsqOltutMc3MY1
```

단순히 파일 읽기임.



### bandit1 -> bandit2

```shell
> cat ./-
CV1DtqXWVFXTvM2F0k09SHz0YwRINYA9
```

역시 파일 읽기이나, - 는 /dev/stdin, /dev/stdout, /dev/stderr 로도 사용될 수 있기 때문에, kernel이 혼동하지 않도록 ./ 상대경로를 붙여서 읽도록 한다.



### bandit2 -> bandit3

```shell
> cat spaces\ in\ this\ filename
UmHadQclWmgdLOKQ3YNgjWxGoRMb5luK
```

파일 이름에 공백과 같은 특수문자가 존재하는 파일 읽기이다.
\를 사용하거나 ""를 사용하여 해결할 수 있다.



### bandit3 -> bandit4

```shell
bandit3@bandit:~$ cd inhere/
bandit3@bandit:~/inhere$ ls -al
total 12
drwxr-xr-x 2 root    root    4096 Oct 16 14:00 .
drwxr-xr-x 3 root    root    4096 Oct 16 14:00 ..
-rw-r----- 1 bandit4 bandit3   33 Oct 16 14:00 .hidden
bandit3@bandit:~/inhere$ cat .hidden 
pIwrPrtPN36QITSp3EQaw936yaFoFgAB
```

디렉토리에 들어가서 숨겨진 파일을 읽어내면 된다.



### bandit4 -> bandit5

> The password for the next level is stored in the only human-readable
> file in the **inhere** directory. 

```shell
bandit4@bandit:~$ cd inhere/
bandit4@bandit:~/inhere$ ls -al
bandit4@bandit:~/inhere$ file ./*
./-file00: data
./-file01: data
./-file02: data
./-file03: data
./-file04: data
./-file05: data
./-file06: data
./-file07: ASCII text
./-file08: data
./-file09: data
bandit4@bandit:~/inhere$ cat ./-file07
koReBOKuIDDepwhWk7jZC0RTdopnAYKh
```

file 명령어를 통해 각 파일들의 정보를 확인한 후, 읽어내면 된다.



### bandit5 -> bandit6

> The password for the next level is stored in a file somewhere under the **inhere** directory and has all of the following properties:
>
> - human-readable
> - 1033 bytes in size
> - not executable

```shell
bandit5@bandit:~/inhere$ ls
maybehere00  maybehere03  maybehere06  maybehere09  maybehere12  maybehere15  maybehere18
maybehere01  maybehere04  maybehere07  maybehere10  maybehere13  maybehere16  maybehere19
maybehere02  maybehere05  maybehere08  maybehere11  maybehere14  maybehere17
bandit5@bandit:~/inhere$ find ./ -readable -size 1033c ! -executable
./maybehere07/.file2
bandit5@bandit:~/inhere$ find ./ -readable -size 1033c ! -executable -exec cat {} \;
DXjZPULLxYr17uwoI01bNLQbtFemEgo7
```

주어진 조건은 읽을 수 있는, 크기가 1033bytes, not executable인 파일이다. 각 각 **find** 명령어의 `-readable`, `-size`, `-executable` 옵션을 이용하여 찾을 수 있는데, 각 각의 옵션에 대한 자세한 사항은 아래와 같이 man page에서 확인할 수 있다. 추가적으로 **find**의 output을 `-exec` 옵션을 이용하여 **cat**을 통해 바로 읽게 할 수 있다.



#### [+]

> #### find 명령어 옵션
>
> ```shell
> bandit5@bandit:~/inhere$ man -k find
> BIO_find_type (3ssl) - BIO chain traversal
> ...
> find (1)             - search for files in a directory hierarchy
> ...
> 
> bandit5@bandit:~/inhere$ man 1 find
> ...
> -readable
> Matches files which are readable.  This takes into account access control lists and other permissions artefacts which the -perm test ignores.  This test makes use of the access(2) system call, and so can be  fooled  by  NFS  servers  which  do UID mapping (or root-squashing), since many systems implement access(2) in the client's kernel and so cannot make use of the UID mapping information held on the server.
> 
> 
> -size n[cwbkMG]
> File uses n units of space, rounding up.  The following suffixes can be used:
> 
> `b'    for 512-byte blocks (this is the default if no suffix is used)
> `c'    for bytes
> `w'    for two-byte words
> `k'    for Kilobytes (units of 1024 bytes)
> `M'    for Megabytes (units of 1048576 bytes)
> `G'    for Gigabytes (units of 1073741824 bytes)
> 
> The size does not count indirect blocks, but it does count blocks in sparse files that are not  actually allocated.  Bear in mind that the `%k' and `%b' format specifiers of -printf handle sparse files differently. The `b' suffix always denotes 512-byte blocks and never 1 Kilobyte blocks, which is different to the behaviour of -ls.
> 
> The  +  and  -  prefixes signify greater than and less than, as usual.  Bear in mind that the size is rounded up to the next unit. Therefore -size -1M is not equivalent to -size  -1048576c. The former only matches empty files, the latter matches files from 1 to 1,048,575 bytes.
> 
> 
> -executable
> Matches files which are executable and directories which are searchable (in a  file  name  resolutionsense).  This takes into account access control lists and other permissions artefacts which the -perm test ignores.  This test makes use of the access(2) system call, and so can be fooled by NFS  servers which do UID mapping (or root-squashing), since many systems implement access(2) in the client's kernel and so cannot make use of the UID mapping information held on the server. Because this  test  is based  only  on  the result of the access(2) system call, there is no guarantee that a file for which
> this test succeeds can actually be executed.
> ...
> ```





### bandit6 -> bandit7

> The password for the next level is stored **somewhere on the server** and has all of the following properties:
>
> - owned by user bandit7
> - owned by group bandit6
> - 33 bytes in size

```shell
bandit6@bandit:~$ find / -user bandit7 -group bandit6 -size 33c 2> /dev/null -exec cat {} \;
HKBPTKQnIay4Fw76bEy8PVxKEDQRKTzs
```

전 문제와 동일하다. **find** 명령어의 `-user`, `-group`, `-size` 옵션을 통해 파일을 찾을 수 있다. / 루트 디렉토리부터 검색하며, `2> /dev/null`을 통해 **stderr**를 화면에 표시하지 않도록 한다.



#### [+]

> #### find 명령어 옵션
>
> ```shell
> -user uname
>       File is owned by user uname (numeric user ID allowed).
> -group gname
>       File belongs to group gname (numeric group ID allowed).
> ```



### bandit7 -> bandit8

> The password for the next level is stored in the file **data.txt** next to the word **millionth**



```shell
bandit7@bandit:~$ ls
data.txt
bandit7@bandit:~$ grep -F "millionth" -A 1 ./data.txt 
millionth	cvX2JJa4CFALtqS87jk27qwqGhBM9plV
comprehend	FKVbjZbVgb0d2RU2DlCqSW049xMITQkB
```

data.txt 안에 존재하는 수 많은 문자열들 중 "millionth"를 찾아내서 그 다음 줄의 값을 확인해야 하므로 __grep__명령어를 사용할 수 있다. `-F`를 사용하여 해당 문자열을 찾아내고, `-A`를 사용하여 matching line 이후 몇 줄을 추가적으로 화면에 표시할 지 설정할 수 있다.

가 아니다. 문제 해석을 잘 못했다. millionth 옆이니 추가적으로 -A 할 필요없고 그냥 `-F` 옵션만 있어도 된다.



#### [+]

> #### grep 명령어 옵션
>
> ```shell
> -F, --fixed-strings
> Interpret PATTERN as a list of fixed strings (instead of regular expressions), separated by newlines, any of which is to be matched.
> 
> -A NUM, --after-context=NUM
> Print NUM lines of trailing context after matching lines.  Places a line containing a group separator (--) between contiguous groups of matches.  With the -o or --only-matching option, this has no effect and a warning is given.
> ```



### bandit8 -> bandit9

> The password for the next level is stored in the file **data.txt** and is the only line of text that occurs only once



```shell
bandit8@bandit:~$ cat data.txt | sort | uniq -u
UsvVyFSfZZWbi6wgC7dAFyFuR6jQQUhR

혹은
bandit8@bandit:~$ cat data.txt | sort | uniq -c
     10 07iR6PwHwihvQ3av1fqoRjICCulpoyms
      1 UsvVyFSfZZWbi6wgC7dAFyFuR6jQQUhR
     10 vBo3qbjNEF2d3meGEkRfc3mKpjtiDz1i
```

__sort__ 명령어를 통해 정렬한 뒤, __uniq__ 명령어를 사용하여 중복된 행을 제거 혹은 중복된 횟수를 count하도록 하여 찾아낼 수 있다.



#### [+]

> #### uniq 명령어 옵션
>
> ```shell
> -c, --count
>       prefix lines by the number of occurrences
> -u, --unique
>       only print unique lines
> ```
>
> 참고: [http://bahndal.egloos.com/576672](#http://bahndal.egloos.com/576672)





### bandit9 -> bandit10

> The password for the next level is stored in the file **data.txt** in one of the few human-readable strings, beginning with several ‘=’ characters.

```shell
bandit9@bandit:~$ strings data.txt | grep "=="
2========== the
========== password
========== isa
========== truKLdjsbJ5g7yyJ2X2R0o3a5HQJFuLk
```

__strings__ 명령어와 __grep__ 명령어의 조합으로 쉽게 찾을 수 있다.



### bandit10 -> bandit11

> The password for the next level is stored in the file **data.txt**, which contains base64 encoded data



```shell
bandit10@bandit:~$ cat data.txt
VGhlIHBhc3N3b3JkIGlzIElGdWt3S0dzRlc4TU9xM0lSRnFyeEUxaHhUTkViVVBSCg==

bandit10@bandit:~$ cat data.txt | base64 --decode
The password is IFukwKGsFW8MOq3IRFqrxE1hxTNEbUPR
```

data.txt 파일은 base64 인코딩된 데이터이므로, __base64__ 명령어를 사용하여 디코딩해준다.



#### [+]

> #### base64 명령어 옵션
>
> ```shell
> -d, --decode
>       decode data
> ```



### bandit11 -> bandit12

> The password for the next level is stored in the file **data.txt**, where all lowercase (a-z) and uppercase (A-Z) letters have been rotated by 13 positions

```shell
bandit11@bandit:~$ cat data.txt | tr 'A-Za-z' 'N-ZA-Mn-za-m'
The password is 5Te8Y4drgCRfCx8ugdwuEX8KFC6k2EUu

bandit11@bandit:~$ cat data.txt | python -c 'import sys; print sys.stdin.read().decode("rot13")'
The password is 5Te8Y4drgCRfCx8ugdwuEX8KFC6k2EUu
```

ROT13을 디코딩하는데에 __tr__ 명령어를 사용할 수 있다. translate의 약자로 지정한 문자를 다른 문자로 치환할 수 있다. 흔히 파일에 존재하는 문자를 모두 대문자로 치환한다던가, 특정 문자만을 제거할 때 사용된다. 자매품으로 python을 이용하여 간단하게 해결할 수도 있다.





### bandit12 -> bandit13

> The password for the next level is stored in the file **data.txt**, which is a hexdump of a file that has been repeatedly compressed. For this level it may be useful to create a directory under /tmp in which you can work using mkdir. For example: mkdir /tmp/myname123.
> Then copy the datafile using cp, and rename it using mv (read the manpages!)

```shell
bandit12@bandit:/tmp$ cp ~/data.txt ./TT
bandit12@bandit:/tmp$ file TT
TT: ASCII text
bandit12@bandit:/tmp$ xxd -r TT > TT1
bandit12@bandit:/tmp$ file TT1
TT1: gzip compressed data, was "data2.bin", last modified: Tue Oct 16 12:00:23 2018, max compression, from Unix
bandit12@bandit:/tmp$ mv TT1.gz
mv: missing destination file operand after 'TT1.gz'
Try 'mv --help' for more information.
bandit12@bandit:/tmp$ mv TT1 TT1.gz
bandit12@bandit:/tmp$ gzip -d TT1.gz
bandit12@bandit:/tmp$ file TT1
TT1: bzip2 compressed data, block size = 900k
bandit12@bandit:/tmp$ mv TT1 TT1.bz2
bandit12@bandit:/tmp$ bzip2 -d TT1.bz2
bandit12@bandit:/tmp$ file TT1
TT1: gzip compressed data, was "data4.bin", last modified: Tue Oct 16 12:00:23 2018, max compression, from Unix
bandit12@bandit:/tmp$ mv TT1 TT1.gz
bandit12@bandit:/tmp$ gzip -d TT1.gz
bandit12@bandit:/tmp$ file TT1
TT1: POSIX tar archive (GNU)
bandit12@bandit:/tmp$ tar -tvf TT1
-rw-r--r-- root/root     10240 2018-10-16 14:00 data5.bin
bandit12@bandit:/tmp$ mv TT1 TT1.tar
bandit12@bandit:/tmp$ tar -xvf TT1.tar
data5.bin
bandit12@bandit:/tmp$ file data5.bin
data5.bin: POSIX tar archive (GNU)
bandit12@bandit:/tmp$ mv data5.bin TT1.tar
bandit12@bandit:/tmp$ tar -xvf TT1.tar
data6.bin
bandit12@bandit:/tmp$ file data6.bin
data6.bin: bzip2 compressed data, block size = 900k
bandit12@bandit:/tmp$ mv data6.bin TT1.bz2
bandit12@bandit:/tmp$ bzip2 -d TT1.bz2
bandit12@bandit:/tmp$ file TT1
TT1: POSIX tar archive (GNU)
bandit12@bandit:/tmp$ mv TT1 TT1.tar
bandit12@bandit:/tmp$ tar -xvf TT1.tar
data8.bin
bandit12@bandit:/tmp$ file data8.bin
data8.bin: gzip compressed data, was "data9.bin", last modified: Tue Oct 16 12:00:23 2018, max compression, from Unix
bandit12@bandit:/tmp$ mv data8.bin TT1.gz
bandit12@bandit:/tmp$ gzip -d TT1.gz
bandit12@bandit:/tmp$ file TT1
TT1: ASCII text
bandit12@bandit:/tmp$ cat TT1
The password is 8ZjyCRiBWFYkneahHwxCv3wb2a1ORpYL
```

하.. 근성으로 해냈다. 나중에 이런 문제를 만났을 경우 __binwalk__라는 갓갓툴을 사용해서 한 큐에 끝내버리도록 하자.



#### [+]

> #### xxd 명령어 옵션
>
> ```shell
> -r | -revert
> reverse operation: convert (or patch) hexdump into binary.  If not writing to stdout, xxd writes into its output file without truncating it. Use the combination -r -p  to  read  plain hexadecimal dumps without line number information and without a particular column layout. Additional Whitespace and line-breaks are allowed anywhere.
> ```
>
> hex dump 파일을 다시 binary 파일로 되돌리는 옵션이다.





### bandit13 -> bandit14

> The password for the next level is stored in **/etc/bandit_pass/bandit14 and can only be read by user bandit14**. For this level, you don’t get the next password, but you get a private SSH key that can be used to log into the next level. **Note:** **localhost** is a hostname that refers to the machine you are working on



```shell
bandit13@bandit:~$ ssh -i sshkey.private bandit14@localhost
Could not create directory '/home/bandit13/.ssh'.
The authenticity of host 'localhost (127.0.0.1)' can't be established.
ECDSA key fingerprint is SHA256:98UL0ZWr85496EtCRkKlo20X3OPnyPSB5tB5RPbhczc.
Are you sure you want to continue connecting (yes/no)? yes
...
bandit14@bandit:~$ cat /etc/bandit_pass/bandit14
4wcYUJFw0k0XLShlDzztnTBHiqxU3b3e
```

개인키 파일이 있다면 가뿐하게 인증이 가능하다. `-i` 옵션을 이용하여 키 파일을 적용한다.



#### [+]

> #### ssh 명령어 옵션
>
> ```shell
> -i identity_file
> Selects a file from which the identity (private key) for public key authentication is read.  The default is ~/.ssh/identity for protocol version 1, and ~/.ssh/id_dsa, ~/.ssh/id_ecdsa, ~/.ssh/id_ed25519 and ~/.ssh/id_rsa for protocol version 2.  Identity files may also be specified on a per-host basis in the configuration file.  It is possible to have multiple -i options (and multiple identities specified in configuration files).  If no certificates have been explicitly specified by the CertificateFile directive, ssh will also try to load certificate information from the filename obtained by appending -cert.pub to identity filenames.
> ```



### bandit14 -> bandit15

> The password for the next level can be retrieved by submitting the password of the current level to **port 30000 on localhost**.

```shell
bandit14@bandit:~$ cat /etc/bandit_pass/bandit14
4wcYUJFw0k0XLShlDzztnTBHiqxU3b3e

bandit14@bandit:~$ nc localhost 30000
4wcYUJFw0k0XLShlDzztnTBHiqxU3b3e
Correct!
BfMYroe26WYalil77FoDi9qh59eK5xNr
```





### bandit15 -> bandit16

> The password for the next level can be retrieved by submitting the password of the current level to **port 30001 on localhost** using SSL encryption.
>
> **Helpful note: Getting “HEARTBEATING” and “Read R BLOCK”? Use -ign_eof and read the “CONNECTED COMMANDS” section in the manpage. Next to ‘R’ and ‘Q’, the ‘B’ command also works in this version of that command…**

```shell
bandit15@bandit:~$ echo "BfMYroe26WYalil77FoDi9qh59eK5xNr" | openssl s_client -connect localhost:30001 -quiet
depth=0 CN = localhost
verify error:num=18:self signed certificate
verify return:1
depth=0 CN = localhost
verify return:1
Correct!
cluFn7wTiGryunymYOu4RcffSxQluehd
```

SSL protocol을 사용해야하니, __openssl__을 사용하여 연결해줄 수 있다. `s_client`는 SSL server에 연결하는 ssl client 프로그램을 실행시키는 명령어이다.  __echo__ 명령어로 문자열을 넘겨주기 위해서는 `-ign-eof` , 혹은 `quiet`를 붙어야하는데, 이는 문자열을 파이프라인을 통해 다 보낼 때까지 세션을 유지하기 위함이다. `-quiet` 옵션은 해당 기능에, 인증서 정보까지 출력하지 않는다.



#### [+]

> #### openssl
>
> ```shell
> DESCRIPTION
> OpenSSL is a cryptography toolkit implementing the Secure Sockets Layer (SSL v2/v3) and Transport Layer Security (TLS v1) network protocols and related cryptography standards required by them.
> 
> s_client
> This implements a generic SSL/TLS client which can establish a transparent connection to a remote server speaking SSL/TLS. It's intended for testing purposes only and provides only rudimentary interface functionality but internally uses mostly all functionality of the OpenSSL ssl library.
> 
> s_server
> This implements a generic SSL/TLS server which accepts connections from remote clients speaking SSL/TLS. It's intended for testing purposes only and provides only rudimentary interface functionality but internally uses mostly all functionality of the OpenSSL ssl library.  It provides both an own command line oriented protocol for testing SSL functions and a simple HTTP response facility to emulate an SSL/TLS-aware webserver.
> ```
>
> 
>
> #### s_client 명령어 옵션
>
> ```shell
> -connect host:port
> This specifies the host and optional port to connect to. If not specified then an attempt is made to connect to the local host on port 4433.
> 
> -ign_eof
> inhibit shutting down the connection when end of file is reached in the input.
> 
> -quiet
> inhibit printing of session and certificate information. This implicitly turns on -ign_eof as well.
> ```





### bandit16 -> bandit17

> The credentials for the next level can be retrieved by submitting the password of the current level to **a port on localhost in the range 31000 to 32000**. First find out which of these ports have a server listening on them. Then find out which of those speak SSL and which don’t. There is only 1 server that will give the next credentials, the others will simply send back to you whatever you send to it.



#### 1 step

__nmap__을 이용하여 열린 포트를 스캔한다. 

```shell
bandit16@bandit:~$ nmap localhost -p31000-32000

Starting Nmap 7.40 ( https://nmap.org ) at 2019-02-26 21:50 CET
Nmap scan report for localhost (127.0.0.1)
Host is up (0.00022s latency).
Not shown: 996 closed ports
PORT      STATE SERVICE
31046/tcp open  unknown
31518/tcp open  unknown
31691/tcp open  unknown
31790/tcp open  unknown
31960/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 0.08 seconds
```

위와 같이 5개의 포트가 열려있음을 확인할 수 있다.



> 포트 지정과 관련된 정보는 man page에서 얻을 수 있다.
>
> ```shell
> -p <port ranges>: Only scan specified ports
>     Ex: -p22; -p1-65535; -p U:53,111,137,T:21-25,80,139,8080,S:9
>     --exclude-ports <port ranges>: Exclude the specified ports from scanning
> ```



#### 2 step

SSL 포트가 열려있는지 확인하기.

```shell
bandit16@bandit:~$ nmap --script ssl-enum-ciphers localhost -p31000-32000

Starting Nmap 7.40 ( https://nmap.org ) at 2019-02-26 22:03 CET
Nmap scan report for localhost (127.0.0.1)
Host is up (0.00021s latency).
Not shown: 996 closed ports
PORT      STATE SERVICE
31046/tcp open  unknown
31518/tcp open  unknown
| ssl-enum-ciphers: 
|   TLSv1.0: 
|     ciphers: 
|       TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA (rsa 1024) - A
| (중략)
|       TLS_RSA_WITH_SEED_CBC_SHA (rsa 1024) - A
|     compressors: 
|       NULL
|     cipher preference: client
|     warnings: 
|       Weak certificate signature: SHA1
|_  least strength: A
31691/tcp open  unknown
31790/tcp open  unknown
| ssl-enum-ciphers: 
|   TLSv1.0: 
|     ciphers: 
|       TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA (rsa 1024) - A
| (중략)
|       TLS_RSA_WITH_CAMELLIA_256_CBC_SHA (rsa 1024) - A
|     cipher preference: client
|     warnings: 
|       Weak certificate signature: SHA1
|_  least strength: A
31960/tcp open  unknown

Nmap done: 1 IP address (1 host up) scanned in 1.38 seconds
```

ssl-enum-ciphers 스크립트를 활용하면 사용된 cipher를 알 수 있다. 이를 이용하여 SSL 프로토콜을 사용하고 있는지 확인이 가능하다. 31518 포트와 31790 포트에서 SSL 프로토콜이 사용됨을 알 수 있다.



> NMAP script의 종류는 다음 링크에서 확인이 가능하다.
>
> [https://nmap.org/nsedoc/index.html](#https://nmap.org/nsedoc/index.html)
>
> #### NMAP SCRIPTING ENGINE (NSE)
>
> ```shell
> The Nmap Scripting Engine (NSE) is one of Nmap's most powerful and flexible features. It allows users to write (and share) simple scripts (using the Lua programming language[11] ) to automate a wide variety of networking tasks. Those scripts are executed in parallel with the speed and efficiency you expect from Nmap. Users can rely on the growing and diverse set of scripts distributed with Nmap, or write their own to meet custom needs.
> ...
> 
> --script filename|category|directory|expression[,...]
> Runs a script scan using the comma-separated list of filenames, script categories, and directories. Each element in the list may also be a Boolean expression describing a more complex set of scripts. Each element is interpreted first as an expression, then as a category, and finally as a file or directory name.
> ```
>
> 
>
> #### ssl-enum-ciphers
>
> ```shell
> This script repeatedly initiates SSLv3/TLS connections, each time trying a new cipher or compressor while recording whether a host accepts or rejects it. The end result is a list of all the ciphersuites and compressors that a server accepts.
> ```



#### 3 step

localhost:31518 에 접속해보면, 입력한 값을 그대로 돌려주는 반면, localhost:31790은 개인 키 값을 돌려준다.
이 개인 키가 bandit17의 개인 키 임을 유추할 수 있으며, 이를 이용하여 bandit17에 접속한 뒤 키 값을 알아낼 수 있다.



##### localhost:31518

```shell
bandit16@bandit:~$ openssl s_client -connect localhost:31518
CONNECTED(00000003)
depth=0 CN = localhost
...
cluFn7wTiGryunymYOu4RcffSxQluehd
cluFn7wTiGryunymYOu4RcffSxQluehd
```



##### localhost:31790

```shell
bandit16@bandit:~$ echo "cluFn7wTiGryunymYOu4RcffSxQluehd" | openssl s_client -connect localhost:31790 -quiet
depth=0 CN = localhost
verify error:num=18:self signed certificate
verify return:1
depth=0 CN = localhost
verify return:1
Correct!
-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAvmOkuifmMg6HL2YPIOjon6iWfbp7c3jx34YkYWqUH57SUdyJ
imZzeyGC0gtZPGujUSxiJSWI/oTqexh+cAMTSMlOJf7+BrJObArnxd9Y7YT2bRPQ
Ja6Lzb558YW3FZl87ORiO+rW4LCDCNd2lUvLE/GL2GWyuKN0K5iCd5TbtJzEkQTu
DSt2mcNn4rhAL+JFr56o4T6z8WWAW18BR6yGrMq7Q/kALHYW3OekePQAzL0VUYbW
JGTi65CxbCnzc/w4+mqQyvmzpWtMAzJTzAzQxNbkR2MBGySxDLrjg0LWN6sK7wNX
x0YVztz/zbIkPjfkU1jHS+9EbVNj+D1XFOJuaQIDAQABAoIBABagpxpM1aoLWfvD
KHcj10nqcoBc4oE11aFYQwik7xfW+24pRNuDE6SFthOar69jp5RlLwD1NhPx3iBl
J9nOM8OJ0VToum43UOS8YxF8WwhXriYGnc1sskbwpXOUDc9uX4+UESzH22P29ovd
d8WErY0gPxun8pbJLmxkAtWNhpMvfe0050vk9TL5wqbu9AlbssgTcCXkMQnPw9nC
YNN6DDP2lbcBrvgT9YCNL6C+ZKufD52yOQ9qOkwFTEQpjtF4uNtJom+asvlpmS8A
vLY9r60wYSvmZhNqBUrj7lyCtXMIu1kkd4w7F77k+DjHoAXyxcUp1DGL51sOmama
+TOWWgECgYEA8JtPxP0GRJ+IQkX262jM3dEIkza8ky5moIwUqYdsx0NxHgRRhORT
8c8hAuRBb2G82so8vUHk/fur85OEfc9TncnCY2crpoqsghifKLxrLgtT+qDpfZnx
SatLdt8GfQ85yA7hnWWJ2MxF3NaeSDm75Lsm+tBbAiyc9P2jGRNtMSkCgYEAypHd
HCctNi/FwjulhttFx/rHYKhLidZDFYeiE/v45bN4yFm8x7R/b0iE7KaszX+Exdvt
SghaTdcG0Knyw1bpJVyusavPzpaJMjdJ6tcFhVAbAjm7enCIvGCSx+X3l5SiWg0A
R57hJglezIiVjv3aGwHwvlZvtszK6zV6oXFAu0ECgYAbjo46T4hyP5tJi93V5HDi
Ttiek7xRVxUl+iU7rWkGAXFpMLFteQEsRr7PJ/lemmEY5eTDAFMLy9FL2m9oQWCg
R8VdwSk8r9FGLS+9aKcV5PI/WEKlwgXinB3OhYimtiG2Cg5JCqIZFHxD6MjEGOiu
L8ktHMPvodBwNsSBULpG0QKBgBAplTfC1HOnWiMGOU3KPwYWt0O6CdTkmJOmL8Ni
blh9elyZ9FsGxsgtRBXRsqXuz7wtsQAgLHxbdLq/ZJQ7YfzOKU4ZxEnabvXnvWkU
YOdjHdSOoKvDQNWu6ucyLRAWFuISeXw9a/9p7ftpxm0TSgyvmfLF2MIAEwyzRqaM
77pBAoGAMmjmIJdjp+Ez8duyn3ieo36yrttF5NSsJLAbxFpdlc1gvtGCWW+9Cq0b
dxviW8+TFVEBl1O4f7HVm6EpTscdDxU+bCXWkfjuRb7Dy9GOtt9JPsX8MBTakzh3
vBgsyi/sN3RqRBcGU40fOoZyfAMT8s1m/uYv52O6IgeuZ/ujbjY=
-----END RSA PRIVATE KEY-----
```



##### connect bandit17@localhost

```shell
bandit16@bandit:~$ echo "cluFn7wTiGryunymYOu4RcffSxQluehd" | openssl s_client -connect localhost:31790 -quiet > /tmp/TT.cert
depth=0 CN = localhost
verify error:num=18:self signed certificate
verify return:1
depth=0 CN = localhost
verify return:1
bandit16@bandit:~$ ls -al /tmp/TT.cert
-rw-r--r-- 1 bandit16 root 1685 Feb 26 22:27 /tmp/TT.cert

bandit16@bandit:~$ ssh -i /tmp/TT.cert bandit17@localhost
...
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@         WARNING: UNPROTECTED PRIVATE KEY FILE!          @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
Permissions 0644 for '/tmp/TT.cert' are too open.
It is required that your private key files are NOT accessible by others.
This private key will be ignored.
Load key "/tmp/TT.cert": bad permissions
...
```

cert 파일을 만든 뒤, 바로 접속하려고 했으나 권한이 너무 열려있어서 접속이 안된다.

__chmod__ 명령어를 이용하여 only user만 rw권한이 있도록 만들어준 뒤 접속한다.

```shell
bandit16@bandit:~$ chmod 600 /tmp/TT.cert
bandit16@bandit:~$ ls -al /tmp/TT.cert
-rw------- 1 bandit16 root 1685 Feb 26 22:27 /tmp/TT.cert
bandit16@bandit:~$ ssh -i /tmp/TT.cert bandit17@localhost
...
bandit17@bandit:~$ cat /etc/bandit_pass/bandit17
xLYVMN9WE5zQ5vHacb0sZEVqbrp7nBTn
```



### bandit17 -> bandit18

> There are 2 files in the homedirectory: **passwords.old and passwords.new**. The password for the next level is in **passwords.new** and is the only line that has been changed between **passwords.old and passwords.new**
>
> **NOTE: if you have solved this level and see ‘Byebye!’ when trying to log into bandit18, this is related to the next level, bandit19**

__diff__ 명령어를 사용하여 두 파일의 차이점을 발견할 수 있다. `-r` 옵션을 줘도 되지만, 디폴트로도 차이점을 제공한다.

```shell
bandit17@bandit:~$ diff passwords.new passwords.old 
42c42
< kfBf3eYk5BPBRzwjqutbbfE887SVc5Yd
---
> hlbSBPAWJmL6WFDb06gpTx1pPButblOA
```

bandit18의 key는 "kfBf3eYk5BPBRzwjqutbbfE887SVc5Yd" 이다.



> #### diff
>
> ```shell
> NAME
>    diff - compare files line by line
> -r, --recursive
>       recursively compare any subdirectories found
> ```
>





### bandit18 -> bandit19

> The password for the next level is stored in a file **readme** in the homedirectory. Unfortunately, someone has modified **.bashrc** to log you out when you log in with SSH.

.bashrc는 bash shell에서 환경설정을 위해 로드하는 파일들 중 하나이다. 사용자가 로그인을 시도하면 인증 과정을 거친 뒤, login shell을 띄워주게 되는데, 이 과정에서 profile, bashrc, .bashrc, .bash_profile... 이런 파일들을 로드한다. login shell을 실행하면서 .profile을 로드하게 되는데, 이걸 실행하면서 .bashrc가 불리게 됨. (login-shell은 우리가 아이디, 패스워드를 입력하고 난 뒤, 뜨는 shell을 말한다.) 

본 문제에서는 bandit18 계정으로 접속해도 바로 byebye하며 종료되는데, 뭐 이건 문제를 다 푼 뒤에 확인한 거지만, .bashrc 파일의 마지막 2줄에 다음과 같은 명령어가 추가되어서 그렇다. 

```sh
echo 'Byebye !'
exit 0
```



이를 우회할 수 있는 방법에 대해서는 여러가지가 있을 수 있겠다. 그 중에 하나로 내가  바로 사용한 방법은 ssh 뒤에 command를 줘서 login shell을 띄워주지 않는 것이다. 저 아래에 있는 ssh man page를 참고하자면, ssh에 명령어를 줄 경우 login shell을 실행하지 않으므로 .bashrc가 실행될 염려가 없다. 

다른 방법으로는 bash shell을 실행시키지 않는 법도 있다. profile과 .profile은 bash shell이 아니더라도 로그인할 경우 모두 적용이 되지만, .bashrc .bash_login .bash_profile의 경우 bash shell이 아닌 경우 적용이 되지 않는다. 따라서, /bin/sh shell을 사용하면 .bashrc가 실행되는 것을 우회할 수 있다.

마지막 방법으로는 ssh는 interactive session을 pseudo-terminal (pty)로 받는데, 이걸 tele-type-writer (tty)로 변경하여 .bashrc 스크립트를 적용하지 않는 것이다. `-T` 옵션을 이용하여 pty를 끄고 tty로 바꿀 수 있다.

```shell
bandit17@bandit:~$ ssh bandit18@localhost ls -al
The authenticity of host 'localhost (127.0.0.1)' can't be established.
ECDSA key fingerprint is SHA256:98UL0ZWr85496EtCRkKlo20X3OPnyPSB5tB5RPbhczc.
Are you sure you want to continue connecting (yes/no)? yes
Failed to add the host to the list of known hosts (/home/bandit17/.ssh/known_hosts).
This is a OverTheWire game server. More information on http://www.overthewire.org/wargames

@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@         WARNING: UNPROTECTED PRIVATE KEY FILE!          @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
Permissions 0640 for '/home/bandit17/.ssh/id_rsa' are too open.
It is required that your private key files are NOT accessible by others.
This private key will be ignored.
Load key "/home/bandit17/.ssh/id_rsa": bad permissions
bandit18@localhost's password: 
total 24
drwxr-xr-x  2 root     root     4096 Oct 16 14:00 .
drwxr-xr-x 41 root     root     4096 Oct 16 14:00 ..
-rw-r--r--  1 root     root      220 May 15  2017 .bash_logout
-rw-r-----  1 bandit19 bandit18 3549 Oct 16 14:00 .bashrc
-rw-r--r--  1 root     root      675 May 15  2017 .profile
-rw-r-----  1 bandit19 bandit18   33 Oct 16 14:00 readme

bandit17@bandit:~$ ssh bandit18@localhost cat readme
The authenticity of host 'localhost (127.0.0.1)' can't be established.
ECDSA key fingerprint is SHA256:98UL0ZWr85496EtCRkKlo20X3OPnyPSB5tB5RPbhczc.
Are you sure you want to continue connecting (yes/no)? yes
Failed to add the host to the list of known hosts (/home/bandit17/.ssh/known_hosts).
This is a OverTheWire game server. More information on http://www.overthewire.org/wargames

@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@         WARNING: UNPROTECTED PRIVATE KEY FILE!          @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
Permissions 0640 for '/home/bandit17/.ssh/id_rsa' are too open.
It is required that your private key files are NOT accessible by others.
This private key will be ignored.
Load key "/home/bandit17/.ssh/id_rsa": bad permissions
bandit18@localhost's password: 
IueksS7Ubh8G3DCwVzrTd8rAVOwq3M5x
```





__If command is specified, it is executed on the remote host instead of a login shell.__ 를 보면 login shell을 실행하지 않고 명령어를 실행함을 알 수 있다. 

> ```shell
> DESCRIPTION
> ssh (SSH client) is a program for logging into a remote machine and for executing commands on a remote machine. It is intended to provide secure encrypted communications between two untrusted hosts over an insecure network. X11 connections, arbitrary TCP ports and UNIX-domain sockets can also be forwarded over the secure channel.
> 
> ssh connects and logs into the specified hostname (with optional user name).  The user must prove his/her identity to the remote machine using one of several methods (see below).
> 
> If command is specified, it is executed on the remote host instead of a login shell.
> 
> If an interactive session is requested ssh by default will only request a pseudo-terminal (pty) for interactive sessions when the client has one. The flags -T and -t can be used to override this behaviour.
> 
> If a pseudo-terminal has been allocated the user may use the escape characters noted below.
> 
> If no pseudo-terminal has been allocated, the session is transparent and can be used to reliably transfer binary data. On most systems, setting the escape character to “none” will also make the session transparent even if a tty is used.
> ```
>
> ##### ssh 명령어 옵션
>
>
> ```shell
>  -T      Disable pseudo-terminal allocation.
> 
>  -t      Force pseudo-terminal allocation.  This can be used to execute
>          arbitrary screen-based programs on a remote machine, which can
>          be very useful, e.g. when implementing menu services.  Multiple
>          -t options force tty allocation, even if ssh has no local tty.
> ```



#### 그 밖의 다양한 풀이들

```shell
bandit17@bandit:~$ ssh bandit18@localhost /bin/sh
bandit17@bandit:~$ ssh bandit18@localhost -t /bin/sh
bandit17@bandit:~$ ssh bandit18@localhost -T
bandit17@bandit:~$ scp bandit18@localhost:readme /tmp/readme
bandit17@bandit:~$ ssh bandit18@localhost "bash --noprofile"
```

scp는 사실상 그냥 명령어 실행시키는거랑 똑같고, bash --noprofile은 profile을 적용시키지 않고 bash shell을 실행시키는 것이다.





### bandit19 -> bandit20

> To gain access to the next level, you should use the setuid binary in the homedirectory. Execute it without arguments to find out how to use it. The password for this level can be found in the usual
> place (/etc/bandit_pass), after you have used the setuid binary.

```shell
bandit19@bandit:~$ ls -al bandit20-do 
-rwsr-x--- 1 bandit20 bandit19 7296 Oct 16 14:00 bandit20-do

bandit19@bandit:~$ ./bandit20-do cat /etc/bandit_pass/bandit20
GbKksEFF4yrVs6il55v6gwY5aVje5f0j
```

superUser 권한이 설정되어 파일이 실행되는 도중만큼은 bandit20의 권한을 갖게 된다. 해당 권한을 갖고 bandit20의 password를 읽으면 클리어.





### bandit20 -> bandit21

> There is a setuid binary in the homedirectory that does the following: it makes a connection to localhost on the port you specify as a commandline argument. It then reads a line of text from the connection and compares it to the password in the previous level (bandit20). If the password is correct, it will transmit the password for the next level (bandit21).
>
> **NOTE:** Try connecting to your own network daemon to see if it works as you think

```shell
bandit20@bandit:~$ nc -l -p 6666 < /etc/bandit_pass/bandit20 &
[1] 15278
bandit20@bandit:~$ ./suconnect 6666
Read: GbKksEFF4yrVs6il55v6gwY5aVje5f0j
Password matches, sending next password
gE269g2h3mw3pwgrj0Ha9Uoqen1c9DGr
[1]+  Done                    nc -l -p 6666 < /etc/bandit_pass/bandit20
```

첨에는 뭔소리지;; 하면서 헤맸는데, 자기가 직접 이전 패스워드를 돌려주는 데몬을 돌려서 연결하면 된다.



> ##### nc 명령어 옵션
>
> ```shell
> -l           
>   listen mode, for inbound connects
> -p 
>   port/ local port number (port numbers can be individual or ranges: lo-hi [inclusive])
> -e 
>   filename/  specify filename to exec after connect (use with caution).  See  the  -c  option for enhanced functionality.
> e 옵션을 이용해서 백도어를 만들 수 있음! ex). nc -e /bin/sh -l -p 6666
> ```





### bandit21 -> bandit22

> A program is running automatically at regular intervals from **cron**, the time-based job scheduler. Look in **/etc/cron.d/** for the configuration and see what command is being executed.

```shell
bandit21@bandit:~$ ls -al /etc/cron.d/
total 24
drwxr-xr-x  2 root root 4096 Oct 16 14:00 .
drwxr-xr-x 88 root root 4096 Oct 16 14:00 ..
-rw-r--r--  1 root root  120 Oct 16 14:00 cronjob_bandit22
-rw-r--r--  1 root root  122 Oct 16 14:00 cronjob_bandit23
-rw-r--r--  1 root root  120 Oct 16 14:00 cronjob_bandit24
-rw-r--r--  1 root root  102 Oct  7  2017 .placeholder
bandit21@bandit:~$ cat /etc/cron.d/cronjob_bandit22
@reboot bandit22 /usr/bin/cronjob_bandit22.sh &> /dev/null
* * * * * bandit22 /usr/bin/cronjob_bandit22.sh &> /dev/null
bandit21@bandit:~$ cat /usr/bin/cronjob_bandit22.sh
#!/bin/bash
chmod 644 /tmp/t7O6lds9S0RqQh9aMcz6ShpAoZKF7fgv
cat /etc/bandit_pass/bandit22 > /tmp/t7O6lds9S0RqQh9aMcz6ShpAoZKF7fgv
bandit21@bandit:~$ cat /tmp/t7O6lds9S0RqQh9aMcz6ShpAoZKF7fgv
Yk7owGAcWjwMVRwrTesJEwB7WVOiILLI
```

cron.d 디렉토리에 있는 파일들은 __crontab__으로 실행을 예약해놓은 파일들이다. 해당 위치의 파일들을 참조하여 예약된 시각에 정해진 행동을 수행한다. bandit22로 예약된 파일의 내용을 보면, cronjob_bandit22.sh 스크립트가 예약되어 있음을 알 수 있다. __crontab__의 man page(5)를 살펴보면, @reboot 이란 것은 시스템이 시작할 때마다, * * * * *은 시간 날짜 요일 불문이다. 결국 해당 스크립트는 실행이 이미 되었을 가능성이 높다. 해당 스크립트의 내용을 보면 bandit22의 패스워드를  /tmp/t7O6lds9S0RqQh9aMcz6ShpAoZKF7fgv에 저장한다. 해당 파일을 읽으면 클리어.



> ##### man 5 crontab
>
> ```shell
>       string         meaning
>       ------         -------
>       @reboot        Run once, at startup.
>       @yearly        Run once a year, "0 0 1 1 *".
>       @annually      (same as @yearly)
>       @monthly       Run once a month, "0 0 1 * *".
>       @weekly        Run once a week, "0 0 * * 0".
>       @daily         Run once a day, "0 0 * * *".
>       @midnight      (same as @daily)
>       @hourly        Run once an hour, "0 * * * *".
> 
> 
> # m h dom mon dow usercommand
> 17 * * * *  root  cd / && run-parts --report /etc/cron.hourly
> 25 6 * * *  root  test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
> 47 6 * * 7  root  test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
> 52 6 1 * *  root  test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )
> #
> ```





### bandit22 -> bandit23

> A program is running automatically at regular intervals from **cron**, the time-based job scheduler. Look in **/etc/cron.d/** for the configuration and see what command is being executed.
>
> **NOTE:** Looking at shell scripts written by other people is a very useful skill. The script for this level is intentionally made easy to read. If you are having problems understanding what it does, try executing it to see the debug information it prints.

```shell
bandit22@bandit:~$ ls /etc/cron.d/
cronjob_bandit22  cronjob_bandit23  cronjob_bandit24
bandit22@bandit:~$ cat /etc/cron.d/cronjob_bandit23
@reboot bandit23 /usr/bin/cronjob_bandit23.sh  &> /dev/null
* * * * * bandit23 /usr/bin/cronjob_bandit23.sh  &> /dev/null
bandit22@bandit:~$ cat /usr/bin/cronjob_bandit23.sh 
#!/bin/bash

myname=$(whoami)
mytarget=$(echo I am user $myname | md5sum | cut -d ' ' -f 1)

echo "Copying passwordfile /etc/bandit_pass/$myname to /tmp/$mytarget"

cat /etc/bandit_pass/$myname > /tmp/$mytarget
bandit22@bandit:~$ whoami
bandit22
bandit22@bandit:~$ echo "I am user bandit23" | md5sum | cut -d ' ' -f 1
8ca319486bfbbc3663ea0fbe81326349
bandit22@bandit:~$ cat /tmp/8ca319486bfbbc3663ea0fbe81326349
jc1udXuA1tiHqjIsL8yaapX5XIAI6i0n
```

앞선 문제와 마찬가지로 예약된 스크립트 cronjob_bandit23.sh를 살펴본다. `myname`값은 스크립트를 실행하는 주체가 bandit23이기 때문에 bandit23이며, `mytarget` 값은 "I am user bandit23"를 __md5sum__을 통해 해쉬 값을 산출해내고, __md5sum__의 결과 값이 `'해쉬 값' + (공백) + '-'` 이여서 __cut__ 명령어를 통해, 공백 기준으로 나눴을 때, 처음으로 나오는 값, 즉 '해쉬 값'이 `mytarget`의 값이다. 따라서 해당 문자열의 해쉬 값을 이름으로 하는 /tmp 디렉토리의 파일을 읽으면 클리어.



> ##### cut 명령어 옵션
>
> ```shell
> -d, --delimiter=DELIM
>   use DELIM instead of TAB for field delimiter
> 
> -f, --fields=LIST
>   select  only these fields;  also print any line that contains no delimiter character, unless the -s option is specified
> ```





### bandit23 -> bandit24

> A program is running automatically at regular intervals from **cron**, the time-based job scheduler. Look in **/etc/cron.d/** for the configuration and see what command is being executed.
>
> **NOTE:** This level requires you to create your own first shell-script. This is a very big step and you should be proud of yourself when you beat this level!
>
> **NOTE 2:** Keep in mind that your shell script is removed once executed, so you may want to keep a copy around…

```shell
bandit23@bandit:~$ ls /etc/cron.d
cronjob_bandit22  cronjob_bandit23  cronjob_bandit24
bandit23@bandit:~$ cat /etc/cron.d/cronjob_bandit24
@reboot bandit24 /usr/bin/cronjob_bandit24.sh &> /dev/null
* * * * * bandit24 /usr/bin/cronjob_bandit24.sh &> /dev/null
bandit23@bandit:~$ cat /usr/bin/cronjob_bandit24.sh 
#!/bin/bash

myname=$(whoami)

cd /var/spool/$myname
echo "Executing and deleting all scripts in /var/spool/$myname:"
for i in * .*;
do
    if [ "$i" != "." -a "$i" != ".." ];
    then
	echo "Handling $i"
	timeout -s 9 60 ./$i
	rm -f ./$i
    fi
done
```

예약된 스크립트를 해석해보면 다음과 같다. 우선, /var/spool/bandit24 디렉토리로 이동한 뒤, 해당 공간에 존재하는 모든 스크립트들 중에서, 파일 이름이 "." 나 ".." 이 아닌 것들을 모두 __timeout__ 명령어를 통해서 제한시간동안 실행시키고 난 뒤 삭제한다. 

여기서 실행시키는 유저는 bandit24이므로 /etc/bandit_pass/bandit24 파일을 충분히 읽을 수 있다. 따라서, 해당 값을 읽어들인 뒤, 내가 읽을 수 있도록 /tmp 파일에 저장시키도록하는 스크립트를 짜서 실행시키도록 한다면 클리어.



/var/spool/bandit24/ 디렉토리에 다음과 같이 스크립트를 작성하도록 한다. tttt.sh 라는 이름으로 작성하였다. 

```sh
bandit23@bandit:/var/spool/bandit24$ vim tttt.sh
#!/bin/bash

myname=$(whoami)

echo "Copying bandit24 passwd to /tmp/TTTT"

cat /etc/bandit_pass/bandit24 > /tmp/TTTT
```



잘 저장한 뒤, bandit24 유저 권한으로 실행될 수 있도록 파일의 권한을 수정해주어야 한다. __chmod__ 명령어를 이용하여 대충 777로 준다. 하고 cronjob_bandit24.sh가 실행되길 기다리면 된다.

```shell
bandit23@bandit:/var/spool/bandit24$ chmod 777 tttt.sh
bandit23@bandit:/var/spool/bandit24$ ls -al tttt.sh
-rwxrwxrwx 1 bandit23 bandit23 118 Feb 28 02:51 tttt.sh
bandit23@bandit:/var/spool/bandit24$ ls -al tttt.sh
ls: cannot access 'tttt.sh': No such file or directory
bandit23@bandit:/var/spool/bandit24$ cat /tmp/TTTT
UoMYTrfrBFHyQXmg6gzctqAwOmw1IohZ
```





### bandit24 -> bandit25

> A daemon is listening on port 30002 and will give you the password for bandit25 if given the password for bandit24 and a secret numeric 4-digit pincode. There is no way to retrieve the pincode except by going through all of the 10000 combinations, called brute-forcing.



```shell
bandit24@bandit:/tmp/TT$ cat tttt.sh 
#!/bin/bash

b24Passwd="UoMYTrfrBFHyQXmg6gzctqAwOmw1IohZ"

for i in {0..9}{0..9}{0..9}{0..9}; do
	echo $b24Passwd $i >> wordlist
done

bandit24@bandit:/tmp/TT$ cat wordlist | nc localhost 30002 > ./resp
bandit24@bandit:/tmp/TT$ grep -v Wrong ./resp 
I am the pincode checker for user bandit25. Please enter the password for user bandit24 and the secret pincode on a single line, separated by a space.
Correct!
The password of user bandit25 is uNG9O58gUE7snukf3bvZ0rxhtnjzSGzG

Exiting.

```

자꾸 중간에 타임아웃이 걸려서 짜증났는데, 두 번정도 나누어서 하니까 됨. timeout 문제가 생기면 wordlist를 0000~5000, 5000~9999로 나누어서 시도해봅시다.

아래는 python script. 근데 너무너무 느림.

```python
bandit24@bandit:/tmp/TT$ cat bf.py 
#!/usr/bin/python

from pwn import *

r = remote('127.0.0.1', 30002)

b24 = "UoMYTrfrBFHyQXmg6gzctqAwOmw1IohZ"
r.recvuntil('\n')
for i in range(5000, 10000):
    message = b24 + ' ' + str(i).zfill(4)
    print 'trying {}...'.format(message)
    r.sendline(message)
    resp = r.recvuntil('\n')
    if resp.find('Wrong') == -1 :
        break

r.interactive()

bandit24@bandit:/tmp/TT$ python bf.py
trying UoMYTrfrBFHyQXmg6gzctqAwOmw1IohZ 8561...
trying UoMYTrfrBFHyQXmg6gzctqAwOmw1IohZ 8562...
trying UoMYTrfrBFHyQXmg6gzctqAwOmw1IohZ 8563...
trying UoMYTrfrBFHyQXmg6gzctqAwOmw1IohZ 8564...
[*] Switching to interactive mode
The password of user bandit25 is uNG9O58gUE7snukf3bvZ0rxhtnjzSGzG

Exiting.
[*] Got EOF while reading in interactive
$  
```

> ##### grep 명령어 옵션
>
> ```shell
> -v, --invert-match
>     Invert the sense of matching, to select non-matching lines. (-v is specified by POSIX .) 
> ```





### bandit25 -> bandit26

> Logging in to bandit26 from bandit25 should be fairly easy… The shell for user bandit26 is not **/bin/bash**, but something else. Find out what it is, how it works and how to break out of it.

bandit25의 홈 디렉토리에는 bandit26.sshkey가 존재한다. 해당 키로 그냥 접속하려고 하면 다음 화면과 같이 접속이 종료된다.

```shell
  _                     _ _ _   ___   __  
 | |                   | (_) | |__ \ / /  
 | |__   __ _ _ __   __| |_| |_   ) / /_  
 | '_ \ / _` | '_ \ / _` | | __| / / '_ \ 
 | |_) | (_| | | | | (_| | | |_ / /| (_) |
 |_.__/ \__,_|_| |_|\__,_|_|\__|____\___/ 
Connection to localhost closed.
```



문제에서 bandit26이 /bin/bash 쉘을 사용하지 않는다고하니 뭐를 사용하는지 확인해본다. /etc/passwd 파일에 계정정보가 담겨있다.

```shell
bandit25@bandit:~$ cat /etc/passwd
...
bandit26:x:11026:11026:bandit level 26:/home/bandit26:/usr/bin/showtext
...

bandit25@bandit:~$ cat /usr/bin/showtext 
#!/bin/sh

export TERM=linux

more ~/text.txt
exit 0
```

확인을 해보면, /bin/bash 대신 /usr/bin/showtext를 실행시키며, 해당 파일은 __more__로 /home/bandit26/text.txt 파일을 읽어준 뒤, 종료한다. bandit26 ascii art가 text.txt에 담겨있는 것 같다.

__more__는 vi 편집기를 기반으로 하며, 화면에 내용을 모두 표출시킨 뒤 종료된다. 다시말해, 화면에 내용이 다 표시되지 않도록 창의 높이를 낮게 위치시킨다면, bandit26의 권한으로 __more__가 실행 중인 상태에 진입할 수 있다. __more__가 실행 중인 상태에서  v를 누르면 vi에 진입할 수 있다. 

vi의 콜론 모드에서 사용할 수 있는 명령어 중 r은 파일을 지정한 커서 위치에 삽입할 수 있는 기능이 있다. 해당 기능을 사용하여 /etc/bandit_pass/bandit26 파일을 삽입하여 패스워드를 알아낼 수 있다.

```shell
:r /etc/bandit_pass/bandit26
...
5czgV9L3Xx8JPOyRbXh6lQbmIOWvPT6Z
...
```

또한, vi에서는 특정 명령어를 실행할 수도 있고, 쉘을 지정하여 실행시킬 수 있는 기능을 가지고 있어, 기존 /usr/bin/showtext로 지정되어 있던 shell을 /bin/bash로 바꿔서 실행시킬 수도 있다.

```shell
:set shell ?
shell=/usr/bin/showtext

:set shell=/bin/bash
:shell
[No write since last change]
bandit26@bandit:~$ cat /etc/bandit_pass/bandit26
5czgV9L3Xx8JPOyRbXh6lQbmIOWvPT6Z
```



>##### more 명령어 
>
>```shell
>v         
>  Start up an editor at current line.  The editor is taken from the environment variable VISUAL if defined,or EDITOR if VISUAL is not defined, or defaults to vi if neither VISUAL nor EDITOR is defined.
>
>SHELL  
>  Current shell in use (normally set by the shell at login time).
>
>VISUAL 
>  The editor the user prefers.  Invoked when command key v is pressed. EDITOR The editor of choice when VISUAL is not specified.
>
>```





### bandit26 -> bandit27

> Good job getting a shell! Now hurry and grab the password for bandit27!

```shell
bandit26@bandit:~$ ls -al bandit27-do
-rwsr-x---  1 bandit27 bandit26 7296 Oct 16 14:00 bandit27-do

bandit26@bandit:~$ ./bandit27-do 
Run a command as another user.
  Example: ./bandit27-do id
  
bandit26@bandit:~$ ./bandit27-do cat /etc/bandit_pass/bandit27
3ba3118a22e93127a4ed485be72ef5ea
```

슈퍼유저 권한이 있다. 그냥 패스워드를 읽어버리면 된다. 문제 출제 의도를 잘 모르겠당;;





### bandit27 -> bandit28

> There is a git repository at `ssh://bandit27-git@localhost/home/bandit27-git/repo`. The password for the user `bandit27-git` is the same as for the user `bandit27`.

```shell
bandit27@bandit:/tmp/TTT$ git clone ssh://bandit27-git@localhost/home/bandit27-git/repo
Cloning into 'repo'...
Could not create directory '/home/bandit27/.ssh'.
The authenticity of host 'localhost (127.0.0.1)' can't be established.
ECDSA key fingerprint is SHA256:98UL0ZWr85496EtCRkKlo20X3OPnyPSB5tB5RPbhczc.
Are you sure you want to continue connecting (yes/no)? yes
Failed to add the host to the list of known hosts (/home/bandit27/.ssh/known_hosts).
This is a OverTheWire game server. More information on http://www.overthewire.org/wargames

bandit27-git@localhost's password: 
remote: Counting objects: 3, done.
remote: Compressing objects: 100% (2/2), done.
remote: Total 3 (delta 0), reused 0 (delta 0)
Receiving objects: 100% (3/3), done.
bandit27@bandit:/tmp/TTT$ ls
repo
bandit27@bandit:/tmp/TTT$ cd repo/
bandit27@bandit:/tmp/TTT/repo$ ls
README
bandit27@bandit:/tmp/TTT/repo$ cat README 
The password to the next level is: 0ef186ac70e04ea33b4c1853d2526fa2
```

저장소를 복제하고 내부에 존재하는 파일을 읽으면 된다.





### bandit28 -> bandit29

> There is a git repository at `ssh://bandit28-git@localhost/home/bandit28-git/repo`. The password for the user `bandit28-git` is the same as for the user `bandit28`.
>
> Clone the repository and find the password for the next level.

```shell
bandit28@bandit:/tmp/TT28$ git clone  ssh://bandit28-git@localhost/home/bandit28-git/repo
Cloning into 'repo'...
Could not create directory '/home/bandit28/.ssh'.
The authenticity of host 'localhost (127.0.0.1)' can't be established.
ECDSA key fingerprint is SHA256:98UL0ZWr85496EtCRkKlo20X3OPnyPSB5tB5RPbhczc.
Are you sure you want to continue connecting (yes/no)? yes
Failed to add the host to the list of known hosts (/home/bandit28/.ssh/known_hosts).
This is a OverTheWire game server. More information on http://www.overthewire.org/wargames

bandit28-git@localhost's password: 
remote: Counting objects: 9, done.
remote: Compressing objects: 100% (6/6), done.
remote: Total 9 (delta 2), reused 0 (delta 0)
Receiving objects: 100% (9/9), done.
Resolving deltas: 100% (2/2), done.
bandit28@bandit:/tmp/TT28$ ls
repo
bandit28@bandit:/tmp/TT28$ cd repo/
bandit28@bandit:/tmp/TT28/repo$ ls
README.md
bandit28@bandit:/tmp/TT28/repo$ cat README.md 
# Bandit Notes
Some notes for level29 of bandit.

## credentials

- username: bandit29
- password: xxxxxxxxxx

```

__git clone__을 통해 Repository를 받으면 위와 같은 정보를 보여준다. password 부분만 지워진 형식이다. 

__git__의 장점은 모든 파일들의 변경사항을 추적할 수 있다는 점이다. 그런 정보들을 다음과 같이 .git 디렉토리에 저장하는데, 이 디렉토리에 있는 정보들을 활용하여 __git__은 사용자에게 해당 레포지토리의 이전 활동 내역 및 변경 사항을 상세하게 제공한다.

__git log__ 명령어를 활용하여 __commit__ 기록을 볼 수 있고, 추가적으로 `-p` 옵션을 통해 상세한 수정사항들을 조회할 수 있다.

```shell
bandit28@bandit:/tmp/TT28/repo$ ls -al
total 16
drwxr-sr-x 3 bandit28 root 4096 Feb 28 11:20 .
drwxr-sr-x 3 bandit28 root 4096 Feb 28 11:20 ..
drwxr-sr-x 8 bandit28 root 4096 Feb 28 11:20 .git
-rw-r--r-- 1 bandit28 root  111 Feb 28 11:20 README.md

bandit28@bandit:/tmp/TT28/repo/.git$ git log -p
commit 073c27c130e6ee407e12faad1dd3848a110c4f95
Author: Morla Porla <morla@overthewire.org>
Date:   Tue Oct 16 14:00:39 2018 +0200

    fix info leak

diff --git a/README.md b/README.md
index 3f7cee8..5c6457b 100644
--- a/README.md
+++ b/README.md
@@ -4,5 +4,5 @@ Some notes for level29 of bandit.
 ## credentials
 
 - username: bandit29
-- password: bbc96594b4e001778eee9975372716b2
+- password: xxxxxxxxxx
```

기존 bbc96594b4e001778eee9975372716b2이었던 패스워드를 xxxxxxx로 변경한 기록을 조회할 수 있다.





### bandit29 -> bandit30

> There is a git repository at `ssh://bandit29-git@localhost/home/bandit29-git/repo`. The password for the user `bandit29-git` is the same as for the user `bandit29`.
>
> Clone the repository and find the password for the next level.

```shell
bandit29@bandit:/tmp/TT29$ git clone ssh://bandit29-git@localhost/home/bandit29-git/repo
Cloning into 'repo'...
Could not create directory '/home/bandit29/.ssh'.
The authenticity of host 'localhost (127.0.0.1)' can't be established.
ECDSA key fingerprint is SHA256:98UL0ZWr85496EtCRkKlo20X3OPnyPSB5tB5RPbhczc.
Are you sure you want to continue connecting (yes/no)? yes
Failed to add the host to the list of known hosts (/home/bandit29/.ssh/known_hosts).
This is a OverTheWire game server. More information on http://www.overthewire.org/wargames

bandit29-git@localhost's password: 
remote: Counting objects: 16, done.
remote: Compressing objects: 100% (11/11), done.
remote: Total 16 (delta 2), reused 0 (delta 0)
Receiving objects: 100% (16/16), done.
Resolving deltas: 100% (2/2), done.
bandit29@bandit:/tmp/TT29$ ls
repo
bandit29@bandit:/tmp/TT29$ cd repo/
bandit29@bandit:/tmp/TT29/repo$ cat README.md 
# Bandit Notes
Some notes for bandit30 of bandit.

## credentials

- username: bandit30
- password: <no passwords in production!>

bandit29@bandit:/tmp/TT29/repo$ git log -p
commit 84abedc104bbc0c65cb9eb74eb1d3057753e70f8
Author: Ben Dover <noone@overthewire.org>
Date:   Tue Oct 16 14:00:41 2018 +0200

    fix username

diff --git a/README.md b/README.md
index 2da2f39..1af21d3 100644
--- a/README.md
+++ b/README.md
@@ -3,6 +3,6 @@ Some notes for bandit30 of bandit.
 
 ## credentials
 
-- username: bandit29
+- username: bandit30
 - password: <no passwords in production!>
 

commit 9b19e7d8c1aadf4edcc5b15ba8107329ad6c5650
Author: Ben Dover <noone@overthewire.org>
Date:   Tue Oct 16 14:00:41 2018 +0200

    initial commit of README.md

diff --git a/README.md b/README.md
new file mode 100644
index 0000000..2da2f39
--- /dev/null
+++ b/README.md
@@ -0,0 +1,8 @@
+# Bandit Notes
+Some notes for bandit30 of bandit.
+
+## credentials
+
+- username: bandit29
+- password: <no passwords in production!>
```

Repository를 받은 뒤, README나 __git log__를 살펴보아도 별다른 것은 발견할 수 없다. 일단 현재 작업 branch에서는 발견할 수 없으니 다른 branch가 존재한다면 해당 branch를 뒤져보는 것이 타당하다.



```shell
bandit29@bandit:/tmp/TT29/repo$ git show-branch --all
* [master] fix username
 ! [origin/HEAD] fix username
  ! [origin/dev] add data needed for development
   ! [origin/master] fix username
    ! [origin/sploits-dev] add some silly exploit, just for shit and giggles
-----
    + [origin/sploits-dev] add some silly exploit, just for shit and giggles
  +   [origin/dev] add data needed for development
  +   [origin/dev^] add gif2ascii
*++++ [master] fix username

bandit29@bandit:/tmp/TT29/repo$ git checkout dev
Branch dev set up to track remote branch dev from origin.
Switched to a new branch 'dev'
bandit29@bandit:/tmp/TT29/repo$ ls -al
total 20
drwxr-sr-x 4 bandit29 root 4096 Feb 28 12:24 .
drwxr-sr-x 3 bandit29 root 4096 Feb 28 12:18 ..
drwxr-sr-x 2 bandit29 root 4096 Feb 28 12:24 code
drwxr-sr-x 8 bandit29 root 4096 Feb 28 12:24 .git
-rw-r--r-- 1 bandit29 root  134 Feb 28 12:24 README.md
bandit29@bandit:/tmp/TT29/repo$ cat README.md 
# Bandit Notes
Some notes for bandit30 of bandit.

## credentials

- username: bandit30
- password: 5b90576bedb2cc04c86a9e924ce42faf

```

추가적으로 dev와 sploits-dev가 발견되었다. sploits-dev는 README.md 파일과 log를 모두 살펴보았지만, 별 다른 것은 없는 반면, dev의 README.md에서는 password가 발견되었다.





### bandit30 -> bandit31

> There is a git repository at `ssh://bandit30-git@localhost/home/bandit30-git/repo`. The password for the user `bandit30-git` is the same as for the user `bandit30`.
>
> Clone the repository and find the password for the next level.

log도 별 특별한 게 없고, branch 조차 master 밖에 없다. git show 명령어를 사용해봤는데, 특별한 게 보였다. tag가 존재했다. __git show__ 명령어를 통해 값을 확인할 수 있다.

```shell
bandit30@bandit:/tmp/TT30/repo$ git show 
HEAD            master          origin/HEAD     origin/master   secret 
bandit30@bandit:/tmp/TT30/repo$ git tag
secret
bandit30@bandit:/tmp/TT30/repo$ git show secret
47e603bb428404d265f59c42920d81e5
```



> ##### tag
>
> tag란 브런치, 커밋의 특정 시점을 나타내기 위해 사용하는 일종의 이름표이다. HEAD와 다르게 고정적이며, 이를 이용해 간편히 과거의 특정 시점으로 되돌릴 수 있다.





### bandit31 -> bandit32

> There is a git repository at `ssh://bandit31-git@localhost/home/bandit31-git/repo`. The password for the user `bandit31-git` is the same as for the user `bandit31`.
>
> Clone the repository and find the password for the next level.

```shell
bandit31@bandit:/tmp/TT31/repo$ cat README.md 
This time your task is to push a file to the remote repository.

Details:
    File name: key.txt
    Content: 'May I come in?'
    Branch: master

```

음 일단 열심히 뒤적뒤적 해보았지만, 별 소득은 없었다. README.md를 자세히 보니 __This time your task is to push a file to the remote repository__가 눈에 크게 띈다. 요구조건대로 May I come in? 이라는 내용을 가진 key.txt를 생성한 뒤, remote repository에 push 하면 클리어.



```shell
bandit31@bandit:/tmp/TT31/repo$ echo "May I come in?" > key.txt
bandit31@bandit:/tmp/TT31/repo$ git add key.txt
The following paths are ignored by one of your .gitignore files:
key.txt
Use -f if you really want to add them.
bandit31@bandit:/tmp/TT31/repo$ git add -f key.txt
bandit31@bandit:/tmp/TT31/repo$ git commit -m "add key.txt"
[master 53dfa50] add key.txt
 1 file changed, 1 insertion(+)
 create mode 100644 key.txt

bandit31@bandit:/tmp/TT31/repo$ git push
Could not create directory '/home/bandit31/.ssh'.
The authenticity of host 'localhost (127.0.0.1)' can't be established.
ECDSA key fingerprint is SHA256:98UL0ZWr85496EtCRkKlo20X3OPnyPSB5tB5RPbhczc.
Are you sure you want to continue connecting (yes/no)? yes
Failed to add the host to the list of known hosts (/home/bandit31/.ssh/known_hosts).
This is a OverTheWire game server. More information on http://www.overthewire.org/wargames

bandit31-git@localhost's password: 
Counting objects: 3, done.
Delta compression using up to 4 threads.
Compressing objects: 100% (2/2), done.
Writing objects: 100% (3/3), 324 bytes | 0 bytes/s, done.
Total 3 (delta 0), reused 0 (delta 0)
remote: ### Attempting to validate files... ####
remote: 
remote: .oOo.oOo.oOo.oOo.oOo.oOo.oOo.oOo.oOo.oOo.
remote: 
remote: Well done! Here is the password for the next level:
remote: 56a9bf19c63d650ce78e6ec0354ee45e
remote: 
remote: .oOo.oOo.oOo.oOo.oOo.oOo.oOo.oOo.oOo.oOo.
remote: 
To ssh://localhost/home/bandit31-git/repo
 ! [remote rejected] master -> master (pre-receive hook declined)
error: failed to push some refs to 'ssh://bandit31-git@localhost/home/bandit31-git/repo'

```





### bandit32 -> bandit33

> After all this `git` stuff its time for another escape. Good luck!

```shell
WELCOME TO THE UPPERCASE SHELL
>> ls
sh: 1: LS: not found
>> $0
$ id
uid=11033(bandit33) gid=11032(bandit32) groups=11032(bandit32)
$ cat /etc/bandit_pass/bandit33
c9c3199ddf4121b10cf581a98d51caee

```

접속하면 굉장히 귀찮게도 입력한 모든 문자를 대문자로 바꿔서 sh로 실행한다. 특수 문자나 숫자는 그대로이니, 대문자를 이름으로 갖고 있는 스크립트를 돌리는 방법과 $변수를 사용하는 방법 등이 있겠다. 

Shell script에서 $0, $1, $2... $@, $# 등은 특별한 값을 갖는 변수로 사용된다. 예를 들어 $0은 스크립트를 실행시킬 때 프로그램의 이름을 포함된 문자열  중 첫 번째를 나타낸다. $1부터는 차례대로 인자들이 저장된다.

bash shell 상에서는 $0은 bash가 저장되어 있는데, 본 문제의 shell 상에서는 sh가 저장되어 있다. 따라서, $0을 입력하면 /bin/sh shell이 실행된다.





### bandit33 -> bandit34

> **At this moment, level 34 does not exist yet.**

끝났당