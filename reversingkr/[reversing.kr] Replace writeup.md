# [reversing.kr] Replace writeup



딱히 뭘 하라고 정해주지는 않은 문제다.

그냥 실행시켜보면 입력 창을 볼 수 있고 숫자를 입력하고  check 버튼을 누르면 특정 동작을 한다.

```assembly
00401171  |.  56                 PUSH ESI                                 ; /pModule
00401172  |.  FF15 14504000      CALL [<&KERNEL32.GetModuleHandleA>]      ; \GetModuleHandleA
00401178  |.  50                 PUSH EAX
00401179  |.  E8 82FEFFFF        CALL Replace.00401000
0040117E  |.  8945 A0            MOV [EBP-60],EAX
00401181  |.  50                 PUSH EAX
00401182  |.  E8 95000000        CALL Replace.0040121C
00401187  |.  8B45 EC            MOV EAX,[EBP-14]
```



자세히 파고들어 가면, 위의 존재하는 `0x004001179`에서 call 한 `0x00401000`에서  `dlgproc`의 파라미터로 준 `0x00401020`이 콜백 함수로 등록되면서 실행되는 구조이다.

```assembly
00401000  /$  8B4424 04          MOV EAX,[ESP+4]
00401004  |.  6A 00              PUSH 0                                   ; /lParam = NULL
00401006  |.  68 20104000        PUSH Replace.00401020                    ; |DlgProc = Replace.00401020
0040100B  |.  6A 00              PUSH 0                                   ; |hOwner = NULL
0040100D  |.  6A 65              PUSH 65                                  ; |pTemplate = 65
0040100F  |.  50                 PUSH EAX                                 ; |hInst
00401010  |.  FF15 A8504000      CALL [<&USER32.DialogBoxParamA>]         ; \DialogBoxParamA
00401016  |.  33C0               XOR EAX,EAX
00401018  \.  C2 1000            RETN 10
0040101B      90                 NOP
```



`0x00401020`에서 부터 점점 창을 완성해가며, 창이 완성된 뒤 숫자를 입력하고 check 버튼을 누르면 다음과 같이 `0x000040105A`에서 GetDlgItemInt를 call 하게 된다. 왜 숫자만 정상적으로 입력되는지 알 수 있다.

check 버튼을 누른 뒤 이 후에 프로그램은 종료가 되어 버리는데(정상적이지는 않음),  `0x00401065`에 존재하는 `CALL Replace.0040466F` 명령어 때문이다. 

```assembly
00401020   .  55                 PUSH EBP
00401021   .  8BEC               MOV EBP,ESP
00401023   .  817D 0C 11010000   CMP DWORD PTR [EBP+C],111
0040102A   .  74 06              JE SHORT Replace.00401032
...
00401032   >  8B45 10            MOV EAX,[EBP+10]
00401035   .  25 FFFF0000        AND EAX,0FFFF
0040103A   .  83E8 02            SUB EAX,2                                ;  Switch (cases 2..3EB)
0040103D   .  74 56              JE SHORT Replace.00401095
0040103F   .  2D E9030000        SUB EAX,3E9
00401044   .  74 06              JE SHORT Replace.0040104C
...
0040104C   > \56                 PUSH ESI                                 ;  Case 3EB of switch 0040103A
0040104D   .  8B75 08            MOV ESI,[EBP+8]
00401050   .  6A 00              PUSH 0                                   ; /IsSigned = FALSE
00401052   .  6A 00              PUSH 0                                   ; |pSuccess = NULL
00401054   .  68 EA030000        PUSH 3EA                                 ; |ControlID = 3EA (1002.)
00401059   .  56                 PUSH ESI                                 ; |hWnd
0040105A   .  FF15 9C504000      CALL [<&USER32.GetDlgItemInt>]           ; \GetDlgItemInt
00401060   .  A3 D0844000        MOV [4084D0],EAX                         ;  input value in EAX
00401065   .  E8 05360000        CALL Replace.0040466F
0040106A   .  33C0               XOR EAX,EAX
```

`0x004084D0` 에 사용자가 입력한 값을 저장한다. 



다음의 `0x0040466f`에 존재할 명령어 때문에, memory access 오류가 발생한다. 코드가 바뀌기 때문에 실제 저 명령어는 아니다.(나중에 memory access를 발생시킬 수 있는 코드로 바뀜) 이 함수는 분석하기가 좀 짜증이 나는데, jump를 코드 중간에 하기 때문에 디스어셈블러 해석이 이상하게 된다.

```assembly
0040466F   $  E8 06000000        CALL Replace.0040467A
00404674      81                 DB 81
00404675   .  05 D0844000        ADD EAX,Replace.004084D0
0040467A   .  C705 16604000 EB609061 MOV DWORD PTR [406016],619060EB
00404684   .  E8 00000000        CALL Replace.00404689
00404689  /$  FF05 D0844000      INC DWORD PTR [4084D0]
0040468F  \.  C3                 RETN
```



위와 같이 생겼지만, 맨 처음 `call 0x40467A` 하여 `0x040467A` -> `0x0404684` -> `0x0404689` -> `0x040468F` -> `0x0404689` -> `0x040468F` -> `0x0404674` 로 돌아가고 `0x0404674` 부터는 다음과 같이 생겼다.

```assembly
00404674   ?  8105D0844000C7051660       add DWORD PTR ds:0x4084d0,0x601605c7
0040467E   ?  40                         INC EAX
0040467F   ?  00EB                       ADD BL,CH
00404681   ?  60                         PUSHAD
00404682   ?  90                         NOP
00404683   ?  61                         POPAD
00404684   .  E8 00000000                CALL Replace.00404689
00404689  /$  FF05 D0844000              INC DWORD PTR [4084D0]
0040468F  \.  C3                         RETN
```

`0x4084d0`에는 사용자의 입력 값+ inc 2번 한 값이 들어가있기 때문에 input + 2 + 0x601605c7 값이 저장되며, 본 함수 내에서 inc를 2번 또 하고, `RETN`을 만나 `0x40106A`로 돌아왔다가, 이번에는 JMP 0x404690으로 다시 `0x40466F` 함수의 내부로 진입하게 된다.

```assembly
00401065   .  E8 05360000                CALL Replace.0040466F
0040106A   .  33C0                       XOR EAX,EAX
0040106C   .  E9 1F360000                JMP Replace.00404690
00401071   >  EB 11                      JMP SHORT Replace.00401084
00401073   .  68 34 60 40 00             ASCII "h4`@",0
00401078   .  68 E9030000                PUSH 3E9                                 ; |ControlID = 3E9 (1001.)
0040107D   .  56                         PUSH ESI                                 ; |hWnd
0040107E   .  FF15 A0504000              CALL [<&USER32.SetDlgItemTextA>]         ; \SetDlgItemTextA
00401084   >  B8 01000000                MOV EAX,1
```



여기서 가장 중요한 명령어는 `MOV DWORD PTR [40466F],C39000C6`이다.

```assembly
00404690   > \A1 D0844000                MOV EAX,[4084D0]
00404695   .  68 9F464000                PUSH Replace.0040469F
0040469A   .  E8 EAFFFFFF                CALL Replace.00404689
0040469F   .  C705 6F464000 C60090C3     MOV DWORD PTR [40466F],C39000C6
004046A9   .  E8 C1FFFFFF                CALL Replace.0040466F
004046AE   .  40                         INC EAX
004046AF   .  E8 BBFFFFFF                CALL Replace.0040466F
004046B4   .  C705 6F464000 E8060000     MOV DWORD PTR [40466F],6E8
004046BE   .  58                         POP EAX
004046BF   .  B8 FFFFFFFF                MOV EAX,-1
004046C4   .^ E9 A8C9FFFF                JMP Replace.00401071
```

위의 저 코드로 인해 `0x40466F` 는 다음과 같이 변한다. EAX에는 `0x4084D0`의 값이 존재하기 때문에 결과적으로 사용자의 input + 2 + 0x601605c7 + 2의 영역에 90 즉 NOP을 채워 넣는다. EAX를 증가시키고 `0x40466F`를 다시 한번 부르기 때문에, 결과적으로 두 바이트에 NOP을 채운다.

```assembly
0040466F   $  C600 90                    MOV BYTE PTR [EAX],90
00404672   ?  C3                         RETN
00404673   ?  0081 05D08440              ADD [ECX+4084D005],AL
```



아니 근데 그래서 이 문제를 어떻게 해결해야지.. 하고 있었는데, 알고 보니 `0x401073`에 있는 명령어가 잘 못 해석이 되고 있었다. 저 명령어는 `push 0x406034` 라고 볼 수 있는데, `0x406034`에는 `Correct!` 라는 문자열이 저장되어 있었다. 즉 저 위치로 가면 Correct! 라는 텍스트 창이 뜰 것이다.

```assembly
00401073   .  68 34 60 40 00             ASCII "h4`@",0

00406034  : 72726F43  Corr
00406038  : 21746365  ect!
```



루프를 보아하니 정상적으로는 접근이 불가하다. 코드를 자세히 살펴보면 아까 살펴봤던 동작인 2 바이트만큼 NOP으로 바꿔준 뒤, 다시 원래대로 `0x40466F` 코드를 바꿔준 뒤, `0x4046C4`에서 `0x401071`로 JUMP 하게 된다. 따라서 `0x401071`의 코드 2 바이트를 NOP으로 바꿔주면 Correct 코드를 실행하게 할 수 있다.

```assembly
0040106C   . /E9 1F360000                JMP Replace.00404690
00401071   > /EB 11                      JMP SHORT Replace.00401084
00401073   . |68 34 60 40 00             ASCII "h4`@",0
00401078   .  68 E9030000                PUSH 3E9                                 ; |ControlID = 3E9 (1001.)
0040107D   .  56                         PUSH ESI                                 ; |hWnd
0040107E   .  FF15 A0504000              CALL [<&USER32.SetDlgItemTextA>]         ; \SetDlgItemTextA
```



따라서 input + 4 + 0x601605c7 = 0x00401071 이 되는 값, 32bit 운영체제에서 산술되는 연산이므로 실제로는 input + 4 + 0x601605c7 = 0x100401071인 값이 될 것이다.  

answer : 2687109798 (A02A0AA6)