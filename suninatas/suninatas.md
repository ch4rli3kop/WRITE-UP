

# Suninatas WRITE-UP

난이도가 쉬워서 웹 처음 공부할 때 좋은 것 같다.



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



### #2 level2

```html
<script>
	function chk_form(){
		var id = document.web02.id.value ;
		var pw = document.web02.pw.value ;
		if ( id == pw )
		{
			alert("You can't join! Try again");
			document.web02.id.focus();
			document.web02.id.value = "";
			document.web02.pw.value = "";
		}
		else
		{
			document.web02.submit();
		}
	}
</script>
<!-- Hint : Join / id = pw -->
<!-- M@de by 2theT0P -->
```

요부분이 중요한 건 알겠는데, 어떻게 하지..  몸부림치다가 Java script는 client side script라서 걍 client 딴에서만 동작하게 된다는 것을 알게 되었다. 그럼 결국 조작할 수 있단 거겟찌

Hint를 보아하니 id와 passwd를 같게 한 뒤, document.web02.submit() 동작을 수행하면 플래그를 얻을 수 있는 것 같다.

원래 burp suite 쓰다가 fiddler는 브라우저만 대상으로 하지 않는다는 정보를 어느 톡방에서 들어서 fiddler로 갈아타게 됬는데, 사용법도 익힐 겸 성심성의껏 작성해본다.

먼저 브포를 걸어 request 전에 값을 수정할 수 있도록 한다.

![slevel2](..\suninatas_image\slevel2.JPG)

브포가 제대로 걸렸으면 대충 아무거나 입력하는데, document.web02.submit()가 실행되야 하므로 반드시 id != pw 한 값으로 입력한다.

![slevel2-1](..\suninatas_image\slevel2-1.JPG)

이후 Join을 클릭하면, document.web02.submit()가 실행되면서 Fiddler에서 브포가 걸린 모습을 확인할 수 있을 것이다. 왼쪽 상단의 Go를 하던가 오른쪽 response란의 Run to Completion을 누르면 끝.

![slevel2-2](..\suninatas_image\slevel2-2.JPG)



style.css가 없어서 오류가 뜨기는 하는데, 굳이 중요한 것은 아니니 넘겨도 된다.



[+] 다른 풀이 방법으로 개발자 도구를 사용하는 방법도 있다. 해당 경우 id와 pw를 같은 값으로 입력한 후, console에서 document.web02.submit()을 실행시키면 된다.





### #3 level3

![slevel3](..\suninatas_image\slevel3.JPG)

??? 하며, 이것저것 뒤져봤는데 별게 없었다. 게다가 Notice 게시판에는 글쓰기 기능이 없다. 글자만 말똥말똥 바라보면서 아니 뭐 하라는거지??하면서 답답할 때는 QnA를 보자. Solver를 보는 것보다 QnA에서 가끔 나오는 깨알같은 단서들을 참고하는게 더 나은 것 같다.



![slevel3-1](..\suninatas_image\slevel3-1.JPG)

이런식으로 문제에 대한 힌트를 얻을 수 있다. 진짜로 Notice Board에 글을 쓸 수 있는 방법이 있는 것 같다. 고수 성님이 말씀하신대로 자유게시판(=QnA 게시판)의 동작을 참고해보며 Notice Board에 쓰는 방법을 찾아보도록 하자.

우선, Q&N 게시판에 접속해보면,

![slevel3-2](..\suninatas_image\slevel3-2.JPG)

처음 저 화면을 보여주기 위해서는 `/board/list.asp?divi=Free`를 요청한다.

![slevel3-3](..\suninatas_image\slevel3-3.JPG)





list.asp가 저렇게 표처럼 정리해주는 것 같다. 

이 후 `WRITE` 버튼을 누르면 다음과 같이 `/board/write.asp?page=1&divi=Free`를 요청하게 된다.

![slevel3-4](..\suninatas_image\slevel3-4.JPG)

다음과 같이 뜸.

![slevel3-5](..\suninatas_image\slevel3-5.JPG)

Board 내용을 대충 작성한 뒤, `SUBMIT`을 누르면 `/board/board_procc.asp`가 실행되면서 게시물이 등록되었다는 팝업 창이 뜨게 된다.

![slevel3-6](..\suninatas_image\slevel3-6.JPG)

![slevel3-7](..\suninatas_image\slevel3-7.JPG)

게시물이 등록되었으면, 이제 다시 `/board/list.asp`를 이용하여 게시물들을 보여준다.

![slevel3-8](..\suninatas_image\slevel3-8.JPG)

![slevel3-9](..\suninatas_image\slevel3-9.JPG)

아마 Notice 게시판도 위와 비슷하게 동작할 것 같다. Notice 게시판에 가보면 다음과 같이 `/board/list.asp?divi=notice`를 요청한다.

![slevel3-10](..\suninatas_image\slevel3-10.JPG)

![slevel3-11](..\suninatas_image\slevel3-11.JPG)

Notice와 Q&A 게시판의 요청을 보면, divi 속성을 이용하여 두 게시판을 구별한다. 그렇다면 아까 Q&A 게시판을 write 할 때 요청한 url에서 divi만 notice로 바꾸면 Notice 게시판에도 글을 쓸 수 있지 않을까?

그리하야 `/board/write.asp?page=1&divi=notice`를 시전해본다.

![slevel3-12](..\suninatas_image\slevel3-12.JPG)

여윽시는 역시 여윽시였따.

![slevel3-13](..\suninatas_image\slevel3-13.JPG)

글을 쓰면 팝업창으로 플래그가 뿅

![slevel3-14](..\suninatas_image\slevel3-14.JPG)![slevel3-15](C:\Users\pch21\Documents\suninatas_image\slevel3-15.JPG)





궁금해서 `/board/view.asp?page=1&divi=notice`로 한번 봐봤더니 다른 사람들이 했던 것들이 보인닿 ㅎ

![slevel3-16](..\suninatas_image\slevel3-16.JPG)







### #4 level4

![slevel4](..\suninatas_image\slevel4.JPG)

```html
				<tr height="30" class="table_main" >
					<td width="120" align="center" bgcolor="cccccc"><font size="2"><b>Point</b></font></td>
					<td width="120" align="center" bgcolor="cccccc"><input type="text" name="total" value="5" size="16"></td>
				</tr>
...
<!-- Hint : Make your point to 50 & 'SuNiNaTaS' -->
<!-- M@de by 2theT0P -->
```

`Plus`를 누를 때마다 Point 값인 value가 증가한다. 힌트를 보아하니 일단 Point를 50으로 증가시켜야 할 것 같다. 뒤에 있는 'SuNiNaTaS'는 뭘 뜻하는지 잘 모르겠다.

`Plus`를 눌렀을 때 요청을 살펴보면 다음과 같다.

![slevel4-1](..\suninatas_image\slevel4-1.JPG)

2번째와 4번째는 인증서파일과 css파일이므로 무시하고, 1번과 3번을 보면, 먼저 `/Part_one/web04/web04_ck.asp`를 요청하는데, response를 보면 그냥 `/Part_one/web04/web04.asp`로 리다이렉트한다. 이 후 `web04.asp`를 요청하면 response로 기존 html 파일에서 value가 1 증가한 html 파일을 보내준다. 

일단 Plus를 연타하던지 fiddler의 composer를 사용해서 요청을 반복하던지 해서 Point를 마구 증가시켜보면, 다음과 같이 Point가 25이상인 경우에는, SuNiNaTaS browser라는 키워드를 제시하며 Point가 더이상 증가하지 않는다.

![slevel4-3](..\suninatas_image\slevel4-3.JPG)

![slevel4-2](..\suninatas_image\slevel4-2.JPG)

흠... User-Agent를 보여주는 것으로 보아, request 하면서 전송되는 User-Agent 정보를 SuNiNaTaS로 바꿔서 server로 하여금 client가 SuNiNaTaS browser를 사용하도록 인식시키라는 것 같다. 

> User-Agent 정보는 브라우저마다 제각각 다른 웹 뷰 디폴트 값을 갖는 문제도 있고, 호환성 문제때문에  서버가 해당 브라우저에 맞는 대응을 해주기 위해 생긴 html header이다. 자세한 정보 =>  https://en.wikipedia.org/wiki/User_agent



Fiddler의 Composer는 반복 요청을 할 때 매우 유용하게 쓸 수 있다. web04_ck.asp를 Composer 란에 끌어놓은 뒤, User-Agent 값을 SuNiNaTaS로 변경하고 Execute 한다. 

![slevel4-4](..\suninatas_image\slevel4-4.JPG)

이제 정상적으로 Point가 증가하는 것을 볼 수 있다.

![slevel4-5](..\suninatas_image\slevel4-5.JPG)

50이 되면 key가 뙇.

![slevel4-6](..\suninatas_image\slevel4-6.JPG)

![slevel4-7](..\suninatas_image\slevel4-7.JPG)











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





