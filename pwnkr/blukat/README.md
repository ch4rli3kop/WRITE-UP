# [pwnable.kr] blukat writeup



#### [summary] group permission

```shell
Sometimes, pwnable is strange...
hint: if this challenge is hard, you are a skilled player.

ssh blukat@pwnable.kr -p2222 (pw: guest)
```

소스 코드는 다음과 같다.

```c
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <fcntl.h>
char flag[100];
char password[100];
char* key = "3\rG[S/%\x1c\x1d#0?\rIS\x0f\x1c\x1d\x18;,4\x1b\x00\x1bp;5\x0b\x1b\x08\x45+";
void calc_flag(char* s){
	int i;
	for(i=0; i<strlen(s); i++){
		flag[i] = s[i] ^ key[i];
	}
	printf("%s\n", flag);
}
int main(){
	FILE* fp = fopen("/home/blukat/password", "r");
	fgets(password, 100, fp);
	char buf[100];
	printf("guess the password!\n");
	fgets(buf, 128, stdin);
	if(!strcmp(password, buf)){
		printf("congrats! here is your flag: ");
		calc_flag(password);
	}
	else{
		printf("wrong guess!\n");
		exit(0);
	}
	return 0;
}
```

password 파일을 읽어와서 buf와 비교한 다음, 값이 동일하다면 password와 key를 xor하여 flag를 출력하는 방식이다.

일단 처음에 눈에 띄는 건 buf는 100 bytes를 할당받은 반면에 128 bytes를 입력 받는다는 것이였다. fp도 덮어쓸 수 있고, ret까지 덮어쓸 수 있다. 다만 canary가 걸려있어 어떻게 우회할 방법이 생각나지 않았다 ㅡㅡ

다음으로는 사실 이건 내가 strcmp를 착각해서 틀린 방법이었는데, \x00을 이용한 우회방법이 떠올랐다. strcmp가 그냥 (인자 하나라도) \x00을 만나면 멈춰서 거기까지만 비교하는 줄 알았는데, 알고보니 두 인자 모두 \x00 즉 null에 도달할 때까지의 문자들을 비교하는 거였다. 하긴 설마 그렇게 취약하게 만들지는 않았겠지

다음 코드의 결과를 보면 strcmp의 동작방식에 대해 파악할 수 있을 것이다.

```c
#include <stdio.h>

int main(int argc, char** argv){
	printf("%d\n", strcmp("\x00aa","aaaa"));
	printf("%d\n", strcmp("a\x00aa", "aaaa"));
	printf("%d\n", strcmp("aaaaaa", "aaaaaaa"));
	printf("%d\n", strcmp("aaaaa","aaaab"));
	return 0;
}
--------------------
1
1
-1
-1
```



다시 문제로 돌아오면, 솔직히 어떻게 풀어야할지 감도 안왔다. 부채널 분석 문제도 아닌 것 같았고.

그러다가 발견했다... 권한이란 것을...

아니 미틴 그룹권한에 blukat_pwn이 있다고?

당연히 의미없는걸 알았지만 cat으로 읽는걸 시도해보긴 했었는데 자연스럽게 permission denied만 보고 넘어갔었는데... 진짜 password 였을 줄이야.

xxd로 시도 안해봤으면 영영 모를 뻔 했다.

```shell
blukat@ubuntu:~$ xxd password 
00000000: 6361 743a 2070 6173 7377 6f72 643a 2050  cat: password: P
00000010: 6572 6d69 7373 696f 6e20 6465 6e69 6564  ermission denied
00000020: 0a  
```



정말 어떻게 이런 아이디어를 내는지 감탄이 절로 나온다 bb



```shell
blukat@ubuntu:~$ cat password | ./blukat 
guess the password!
congrats! here is your flag: Pl3as_DonT_Miss_youR_GrouP_Perm!!
```



