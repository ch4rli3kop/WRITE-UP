# [codeengn] Basic RCE L01 writeup



코드엔진 문제를 조금씩 풀어보기로 했다.

1번 문제는 옛날에 봤던 abex 문제임

```shell
HDD를 CD-Rom으로 인식시키기 위해서는 GetDriveTypeA의 리턴값이 무엇이 되어야 하는가
```



코드를 살펴보면 다음과 같다. `0x0401018`에서 호출하는 `GetDriveTypeA` 함수의 리턴 값에 따라서 분기문이 결정되는 것을 알 수 있다. 

```assembly
00401000 >/$  6A 00         PUSH 0                                   ; /Style = MB_OK|MB_APPLMODAL
00401002  |.  68 00204000   PUSH 01.00402000                         ; |Title = "abex' 1st crackme"
00401007  |.  68 12204000   PUSH 01.00402012                         ; |Text = "Make me think your HD is a CD-Rom."
0040100C  |.  6A 00         PUSH 0                                   ; |hOwner = NULL
0040100E  |.  E8 4E000000   CALL <JMP.&USER32.MessageBoxA>           ; \MessageBoxA
00401013  |.  68 94204000   PUSH 01.00402094                         ; /RootPathName = "c:\"
00401018  |.  E8 38000000   CALL <JMP.&KERNEL32.GetDriveTypeA>       ; \GetDriveTypeA
0040101D  |.  46            INC ESI
0040101E  |.  48            DEC EAX
0040101F  |.  EB 00         JMP SHORT 01.00401021
00401021  |>  46            INC ESI
00401022  |.  46            INC ESI
00401023  |.  48            DEC EAX
00401024  |.  3BC6          CMP EAX,ESI
00401026  |.  74 15         JE SHORT 01.0040103D
00401028  |.  6A 00         PUSH 0                                   ; /Style = MB_OK|MB_APPLMODAL
0040102A  |.  68 35204000   PUSH 01.00402035                         ; |Title = "Error"
0040102F  |.  68 3B204000   PUSH 01.0040203B                         ; |Text = "Nah... This is not a CD-ROM Drive!"
00401034  |.  6A 00         PUSH 0                                   ; |hOwner = NULL
00401036  |.  E8 26000000   CALL <JMP.&USER32.MessageBoxA>           ; \MessageBoxA
0040103B  |.  EB 13         JMP SHORT 01.00401050
0040103D  |>  6A 00         PUSH 0                                   ; |/Style = MB_OK|MB_APPLMODAL
0040103F  |.  68 5E204000   PUSH 01.0040205E                         ; ||Title = "YEAH!"
00401044  |.  68 64204000   PUSH 01.00402064                         ; ||Text = "Ok, I really think that your HD is a CD-ROM! :p"
00401049  |.  6A 00         PUSH 0                                   ; ||hOwner = NULL
0040104B  |.  E8 11000000   CALL <JMP.&USER32.MessageBoxA>           ; |\MessageBoxA
00401050  \>  E8 06000000   CALL <JMP.&KERNEL32.ExitProcess>         ; \ExitProcess
```

근데 분기문을 결정하는게 EAX 값이랑 ESI 값을 비교하는 건데, ESI에는 00401000이 들어가있다. 일부러 저렇게 만들었는지는 몰라도 그냥 그렇다고...



`GetDriveTypeA` 함수의 리턴 값을 살펴보면 CDROM인 경우 어떤 값을 리턴하는지 알 수 있다.

| Return code/value       | Description                                                  |
| ----------------------- | ------------------------------------------------------------ |
| **DRIVE_UNKNOWN** 0     | The drive type cannot be determined.                         |
| **DRIVE_NO_ROOT_DIR** 1 | The root path is invalid; for example, there is no volume mounted at the specified path. |
| **DRIVE_REMOVABLE** 2   | The drive has removable media; for example, a floppy drive, thumb drive, or flash card reader. |
| **DRIVE_FIXED** 3       | The drive has fixed media; for example, a hard disk drive or flash drive. |
| **DRIVE_REMOTE** 4      | The drive is a remote (network) drive.                       |
| **DRIVE_CDROM** 5       | The drive is a CD-ROM drive.                                 |
| **DRIVE_RAMDISK** 6     |                                                              |

https://docs.microsoft.com/en-us/windows/desktop/api/fileapi/nf-fileapi-getdrivetypew

