## [bytebandits 2020] baby_rust writeup

#### [Summary] rust reversing

```shell
ch4rli3kop at ubuntu in ~/WRITE-UP/bytebandits2020/baby_rust
$ ./chall 
AAAAAAAAA
you fail
```

대충 위와같이 동작하는 프로그램



### Analysis

`sub_0053A0()` 함수가 키 포인트다. 0x0543D에 존재하는 `sub_0092A0()`을 통해 사용자의 입력을 받는다.

힙을 할당하여 사용자의 입력 값을 저장하는데, 이후 힙 할당을 하고 사용자의 입력 값을 복사하는 작업을 두 번정도 한다. (아마 rust 상의 function을 이동할 때마다 새로운 힙에 데이터를 복사하는 것 같다.)



그리고 사용자의 입력은 0x054A8에 위치한 다음의 루틴에서 연산된다. 사용자의 입력과 7부터 1씩 증가시킨 값과 xor 연산을 하는 모습이다.

```c
 do
    {
      v9 = v6[idx] ^ (idx + 7);
      if ( v7 == (void **)v14 )
      {
        alloc_new_process((__int64)&v13, (__int64)v7, 1uLL);
        v7 = (void **)*((_QWORD *)&v14 + 1);
      }
      ++idx;
      *((_BYTE *)v7 + (_QWORD)v13) = v9;
      v7 = (void **)++*((_QWORD *)&v14 + 1);
    }

...
    
    
  if ( v23 == v7 )
  {
    v10 = 0LL;
    while ( v7 != v10 )
    {
      v11 = *((_BYTE *)v10 + (_QWORD)v21) == *((_BYTE *)v10 + (_QWORD)v13);
      v10 = (void **)((char *)v10 + 1);
      if ( !v11 )
        goto LABEL_15;
    }
    *(_QWORD *)&flag = &off_343F0;
    *((_QWORD *)&flag + 1) = 1LL;
    v16 = 0LL;
    v17 = "you fail\n"
          "assertion failed: `(left == right)`\n"
          "  left: ``,\n"
          " right: ``: destination and source slices have different lengths";
    v18 = 0LL;
    sub_A0D0(&flag, v7);
  }
```

0x005507에 존재하는 `cmp     [rsp+0C8h+var_48], rsi`에서 키 길이를 체크한다. 0x31을 비교하였음.

0x005529에 존재하는 `cmp     bl, [rax+rdx]`에서 연산한 결과 값을 특정 문자열과 비교하는 것을 볼 수 있는데, 해당 결과가 모두 참이어야 성공루틴으로 들어가는 것을 볼 수 있음.



### FLAG

```python
a = 'adhmp`badO|sL}JuvvFmiui{@IO}QQVRZ'
result = ''
for i in range(7, 0x21+7):
    result += chr(ord(a[i-7]) ^ i)
print(result)

# flag{look_ma_i_can_write_in_rust}
```







