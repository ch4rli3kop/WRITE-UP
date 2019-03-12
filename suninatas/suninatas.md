# Suninatas WRITE-UP





## Web

### #1 level1

```php
<%
    str = Request("str")

    If not str = "" Then
        result = Replace(str,"a","aad")
        result = Replace(result,"i","in")
        result1 = Mid(result,2,2)
        result2 = Mid(result,4,6)
        result = result1 & result2
        Response.write result
        If result = "admin" Then
            pw = "????????"
        End if
    End if
%>
```

요약해보면 `a->aad`, `i->in`이고 Mid(result, 2, 2)는 result가 `abcde`라면 `bc`를 리턴하는 함수이다. `result = result1 & result2`는 그냥 두 문자열을 이어주는 거라고 생각하면 될 것 같다.

위의 조건들에 부합하는 적당한 문자열 `ami`를 입력해주면 Solve.





## forensic

### #14 Do you know password of suninatas?

summary : decrypt /etc/shadow SHA512

#### /etc/shadow

```shell
root:$6$E2loH6yC$0lcZ0hG/b.YqlsPhawt5NtX2jJkSFBK6eaF/wa46d8/3KPs6d45jNHgNoJOl7X1RsOrYsZ.J/BBexJ93ECVfW.:15426:0:99999:7:::
...
suninatas:$6$QlRlqGhj$BZoS9PuMMRHZZXz1Gde99W01u3kD9nP/zYtl8O2dsshdnwsJT/1lZXsLar8asQZpqTAioiey4rKVpsLm/bqrX/:15427:0:99999:7:::
```

passwd 파일과 shadow 파일을 주는데, shadow 파일의 경우 root와 suninatas 계정의 해쉬 처리된 패스워드 값을 확인할 수 있다. SHA-512를 사용했으며, salt 값으로 `QlRlqGhj`를 사용하였다.

online decrypter를 찾아봤으나, 제대로 되는 것이 없어 결국 john the ripper를 사용했다. 다행히 john으로 쉽게 구할 수 있다.



#### hash crack

```shell
> sudo apt install john
...

> john --show shadow
root:toor:15426:0:99999:7:::
suninatas:iloveu1:15427:0:99999:7:::

2 password hashes cracked, 0 left
```

root와 suninatas의 패스워드를 구했다. 답은 suninatas의 패스워드인 `iloveu1`이다.





> shadow 파일의 구조는 다음과 같다.
>
> ```shell
> Username : It is your login name.
> Password : It is your encrypted password. The password should be minimum 8-12 characters long including special characters, digits, lower case alphabetic and more. Usually password format is set to $id$salt$hashed, The $id is the algorithm used On GNU/Linux as follows:
> 
>     $1$ is MD5
>     $2a$ is Blowfish
>     $2y$ is Blowfish
>     $5$ is SHA-256
>     $6$ is SHA-512
> 
> Last password change (lastchanged) : Days since Jan 1, 1970 that password was last changed
> Minimum : The minimum number of days required between password changes i.e. the number of days left before the user is allowed to change his/her password
> Maximum : The maximum number of days the password is valid (after that user is forced to change his/her password)
> Warn : The number of days before password is to expire that user is warned that his/her password must be changed
> Inactive : The number of days after password expires that account is disabled
> Expire : days since Jan 1, 1970 that account is disabled i.e. an absolute date specifying when the login may no longer be used
> ```
>
> reference : https://www.cyberciti.biz/faq/understanding-etcshadow-file/





### #15 Do you like music? Hint : AuthKey is in this file.

summary : search meta data

`diary.mp3` 파일을 얻을 수 있다. 처음에는 스펙토그램 문제인 줄 알고 삽질했는데, 속성 창에 있는 메타 정보를 읽는 문제였다.

윈도우 기준 `파일 -> 속성 -> 자세히`로 보면 지휘자 항목에 `GoodJobMetaTagSearch`를 볼 수 있다. 해당 값이 키임





## misc

### #13 KEY Finding

현재 프레임의 소스를 보면 다음과 같은 힌트를 볼 수 있다.

```html
<!--	Hint : 프로그래머의 잘못된 소스백업 습관 -->
<!--	Hint : The programmer's bad habit of backup source codes -->
```

???하며 좀 많이 헤맸다. http://suninatas.com/Part_one/web13/web13.zip 에서 web13.zip 파일을 가져올 수 있다.

이 zip 파일에는 암호가 걸려있는데, 4글자라고 하니 Brute-force로 때려박아서 얻을 수 있다.

적당히 john-the-ripper를 사용토록 하자. zip2john은 official로서 지원하지는 않는다. 설치는 https://chp747.tistory.com/213?category=716904를 참고하도록 하자.

```shell
> ../JohnTheRipper/run/zip2john web13.zip > test.john
ver 2.0 web13.zip/whitehack1.jpg PKZIP Encr: cmplen=3974, decmplen=4017, crc=B1329C55
ver 2.0 web13.zip/whitehack2.jpg PKZIP Encr: cmplen=58089, decmplen=58427, crc=EFA45D9D
ver 2.0 web13.zip/whitehack3.jpg PKZIP Encr: cmplen=3954, decmplen=3937, crc=4A3CF125
ver 2.0 web13.zip/whitehack4.jpg PKZIP Encr: cmplen=7003, decmplen=7069, crc=E4023BA9
ver 2.0 NOTE: It is assumed that all files in each archive have the same password.
If that is not the case, the hash may be uncrackable. To avoid this, use
option -o to pick a file at a time.

> ../JohnTheRipper/run/john --incremental test.john --pot=test.pot
Warning: invalid UTF-8 seen reading test.john
Using default input encoding: UTF-8
Loaded 1 password hash (PKZIP [32/64])
Will run 8 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
7642             (web13.zip)
1g 0:00:00:06 DONE (2019-03-13 05:32) 0.1490g/s 8582Kp/s 8582Kc/s 8582KC/s 08r..sapphine
Use the "--show" option to display all of the cracked passwords reliably
Session completed

> cat test.pot
$pkzip2$3*1*1*0*8*24*b132*b655*fbc3801ab16804b8b1511358a763de830c1f53d33747025d8a0ea79915a3173d8b8d6b18*1*0*8*24*efa4*b6a9*fbc3801ab16804b8b15185f3e7774bb635c23e916859e05ae64f2da2331ffff1f66faeb4*2*0*35*24*f3e4e327*11df4*35*8*35*f3e4*b2f4*fbc3801ab16804b8b151c51c311292a47cede4d9dd82a4c3f42c7b5872daf579c6e4aa2af761b8107d80fb1ae9ce257b831b807687*$/pkzip2$:7642
```

passwd : 7642를 사용하여 압축을 풀면 4개의 jpg 파일과 1개의 txt 파일이 나오는데, txt 파일의 내용은 다음과 같다.

```
4개의 이미지를 합하여 key를 구하시오
```



파일들에서 "key"를 키워드로 하여 문자열을 검색해서 나온 결과를 모두 합치면 Solve.

```shell
 ch4rli3kop@ch4rli3kop-pc  /mnt/d/Download/web13  strings * | grep "key"
first key : 3nda192n
second key : 84ed1cae
third key: 8abg9295
fourth key : cf9eda4d
 key
```





