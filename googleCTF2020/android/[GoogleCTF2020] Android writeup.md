# [GoogleCTF2020] Android writeup

### Summary 

- Rev
- reverse.apk
- Extended Euclidean algorithm



## com.google.ctf.sandbox.ő

일단 다음과 같이 뻐킹하게도 디컴파일이 안됨.

```java
package com.google.ctf.sandbox;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

/*  JADX ERROR: NullPointerException in pass: ExtractFieldInit
    java.lang.NullPointerException
    	at jadx.core.utils.BlockUtils.isAllBlocksEmpty(BlockUtils.java:564)
    	at jadx.core.dex.visitors.ExtractFieldInit.getConstructorsList(ExtractFieldInit.java:245)
    	at jadx.core.dex.visitors.ExtractFieldInit.moveCommonFieldsInit(ExtractFieldInit.java:126)
    	at jadx.core.dex.visitors.ExtractFieldInit.visit(ExtractFieldInit.java:46)
    */
/* renamed from: com.google.ctf.sandbox.ő  reason: contains not printable characters */
public class C0000 extends Activity {

    /* renamed from: class  reason: not valid java name */
    long[] f0class;

    /* renamed from: ő  reason: contains not printable characters */
    int f1;

    /* renamed from: ő  reason: contains not printable characters and collision with other field name */
    long[] f2;

    /* access modifiers changed from: protected */
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        final EditText editText = (EditText) findViewById(R.id.editText);
        final TextView textView = (TextView) findViewById(R.id.textView);
        ((Button) findViewById(R.id.button)).setOnClickListener(new View.OnClickListener() {
            /*  JADX ERROR: Method load error
                jadx.core.utils.exceptions.DecodeException: Load method exception: Not class type: long in method: com.google.ctf.sandbox.?.1.onClick(android.view.View):void, dex: classes.dex
                	at jadx.core.dex.nodes.MethodNode.load(MethodNode.java:151)
                	at jadx.core.dex.nodes.ClassNode.load(ClassNode.java:286)
                	at jadx.core.dex.nodes.ClassNode.load(ClassNode.java:292)
                	at jadx.core.ProcessClass.process(ProcessClass.java:36)
                	at jadx.core.ProcessClass.generateCode(ProcessClass.java:58)
                	at jadx.core.dex.nodes.ClassNode.decompile(ClassNode.java:273)
                Caused by: jadx.core.utils.exceptions.JadxRuntimeException: Not class type: long
                	at jadx.core.dex.info.ClassInfo.checkClassType(ClassInfo.java:60)
                	at jadx.core.dex.info.ClassInfo.fromType(ClassInfo.java:31)
                	at jadx.core.dex.info.ClassInfo.fromDex(ClassInfo.java:44)
                	at jadx.core.dex.nodes.MethodNode.initTryCatches(MethodNode.java:328)
                	at jadx.core.dex.nodes.MethodNode.load(MethodNode.java:139)
                	... 5 more
                */
            public void onClick(android.view.View r1) {
                /*
                // Can't load method instructions: Load method exception: Not class type: long in method: com.google.ctf.sandbox.ő.1.onClick(android.view.View):void, dex: classes.dex
                */
                throw new UnsupportedOperationException("Method not decompiled: com.google.ctf.sandbox.C0000.AnonymousClass1.onClick(android.view.View):void");
            }
        });
    }
}
```



처음에는 smali 코드만을 보고 분석했으나, 우선 뻐킹한 특수문자 ő 때문에, reference 등의 기능들도 제대로 수행되지가 않았음.

우선 해당 ő를 o로 변경한 뒤 다시 빌드해서 분석을 진행했음. 바꾸는건 이 아저씨꺼 참고함. [링크](https://github.com/luker983/google-ctf-2020/tree/master/reversing/android)

```shell
$ apktool d reverse.apk
$ find reverse/AndroidManifest.xml -type f | xargs gsed -i 's/ő/o/g'
$ find reverse/smali/ -type -f | xargs gsed -i 's/ő/o/g'
$ find reverse/ -name "*ő*" -exec rename 's/ő/o/g' {} ";"
$ apktool b reverse -o replaced.apk
```



해당 파일로는 여전히 디컴파일이 제대로 수행되지 않는 것으로 보아 다분히 의도한 것인듯함.

ghidra가 아주 상당히 매우 괜찮은 apk 디컴파일 기능을 지원하는 것을 깨닫고 요걸로 분석을 진행함.

다만 smali 코드를 보는 것은 불편하기에 왓다갓다하면서 봤음.



## com.google.ctf.sandbox.o::onCreate()

onCreate()의 경우 다음과 같이 디컴파일이 진행됨.

```java
void onCreate(o this,Bundle savedInstanceState)

{
  View pVVar1;
  View pVVar2;
  View ref;
  View$OnClickListener ref_00;
  
  super.onCreate(savedInstanceState);
  this.setContentView(0x7f050000);
  pVVar1 = this.findViewById(0x7f040006);
  checkCast(pVVar1,EditText);
  pVVar2 = this.findViewById(0x7f040015);
  checkCast(pVVar2,TextView);
  ref = this.findViewById(0x7f040002);
  checkCast(ref,Button);
  ref_00 = new View$OnClickListener(this,pVVar1,pVVar2);
  ref.setOnClickListener(ref_00);
  return;
}
```

smali 코드로 자세히 살펴보면, 다음과 같이 com/google/ctf/sandbox/o$1 클래스를 사용하는 것을 확인할 수 있음.

```java
    .line 39
    .local v2, "button":Landroid/widget/Button;
    new-instance v3, Lcom/google/ctf/sandbox/o$1;

    invoke-direct {v3, p0, v0, v1}, Lcom/google/ctf/sandbox/o$1;-><init>(Lcom/google/ctf/sandbox/o;Landroid/widget/EditText;Landroid/widget/TextView;)V

    invoke-virtual {v2, v3}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V
```



## com.google.ctf.sandbox.o$1::onClick

o$1 클래스의 onClick 함수를 살펴보면 ghidra가 다음과 같이 디컴파일 해줌.

```java

void onClick(o$1 this,View v)

{
  boolean bVar1;
  char cVar2;
  Integer pIVar3;
  Editable ref;
  String ref_00;
  String pSVar4;
  Object[] ppOVar5;
  StringBuilder ref_01;
  EditText ref_02;
  TextView ref_03;
  int iVar6;
  Object ref_04;
  
  this.this$0.o = 0;
  ppOVar5 = new Object[0x31];
  pIVar3 = Integer.valueOf(0x41);
  ppOVar5[0] = pIVar3;
  pIVar3 = Integer.valueOf(0x70);
  ppOVar5[1] = pIVar3;
  pIVar3 = Integer.valueOf(0x70);
  ppOVar5[2] = pIVar3;

    ...
  
  pIVar3 = Integer.valueOf(0x6f);
  ppOVar5[0x2e] = pIVar3;
  pIVar3 = Integer.valueOf(0x6e);
  ppOVar5[0x2f] = pIVar3;
  pIVar3 = Integer.valueOf(0x3f);
  ppOVar5[0x30] = pIVar3;
  ref_01 = new StringBuilder();
  iVar6 = 0;
  while (iVar6 < ppOVar5.length) {
    ref_04 = ppOVar5[iVar6];
    checkCast(ref_04,Character);
    cVar2 = ref_04.charValue();
    ref_01.append(cVar2);
    iVar6 = iVar6 + 1;
  }
  ref_02 = this.val$editText;
  ref = ref_02.getText();
  ref_00 = ref.toString();
  pSVar4 = ref_01.toString();
  bVar1 = ref_00.equals(pSVar4);
  if (bVar1 == false) {
    ref_03 = this.val$textView;
    ref_03.setText("❌");
  }
  else {
    ref_03 = this.val$textView;
    ref_03.setText("🚩");
  }
  return;
}
```

그러나 위의 내용에서는 플래그가 "Apparently this is not the flag. What's going on?"을 입력했을 경우에만 나타남. 추가적인 분석이 필요했음.

그러나 smali 코드와 비교하며 코드를 분석하면서 이상한 부분을 발견했음. 정상적인 flow에서는 나타나지 않는 Error Exception을 처리해주는 부분이 있는 것을 확인함.

```shell
* Class: Lcom/google/ctf/sandbox/o$1;                        *
* Class Access Flags:                                        *
*                                                            *
* Superclass: Ljava/lang/Object;                             *
* Interfaces:                                                *
*         Landroid/view/View$OnClickListener;                *
* Source File: ő.java                                        *
*                                                            *
* Method Signature: V( Landroid/view/View;                   *
*          )                                                 *
* Method Access Flags:                                       *
*         ACC_PUBLIC                                         *
*                                                            *
* Method Register Size: 20                                   *
* Method Incoming Size: 2                                    *
* Method Outgoing Size: 4                                    *
* Method Debug Info Offset: 0x1d40b                          *
* Method ID Offset: 0x81e0                                   *
*                                                            *
**************************************************************
    void __stdcall onClick(o$1 * this, View * v)
             void              <VOID>         <RETURN>
             o$1 *             iv0:4          this
             View *            iv1:4          v
             undefined4        v0:4           local_0
             undefined4        v1:4           local_1
             undefined4        v2:4           local_2
             undefined4        v3:4           local_3
             undefined4        v4:4           local_4
             undefined4        v5:4           local_5
             undefined4        v6:4           local_6
             undefined4        v7:4           local_7
             undefined4        v8:4           local_8
             undefined4        v9:4           local_9
             undefined4        v10:4          local_10
             undefined4        v11:4          local_11
             undefined4        v12:4          local_12
             undefined4        v13:4          local_13
             undefined4        v14:4          local_14
             undefined4        v15:4          local_15
             undefined4        v16:4          local_16
             undefined4        v17:4          local_17
      com::google::ctf::sandbox::o$1::onClick         XREF[2]:     Entry Point(*), e0001028(*)  
        50037348 08 01 12 00     move_obj   local_1,v18
        5003734c 54 12 1d 05     iget_obj   local_2,[local_1:this$0_1309]                    com::google::ctf::sandbox::o$1::
        50037350 12 03           const_4    local_3,0x0
        50037352 59 23 21 05     iput       local_3,[local_2:o]                              com::google::ctf::sandbox::o::o
        50037356 13 02 31 00     const_16   local_2,0x31
        5003735a 12 03           const_4    local_3,0x0
        5003735c 12 34           const_4    local_4,0x3
        5003735e 12 25           const_4    local_5,0x2
        50037360 12 16           const_4    local_6,0x1
        50037362 12 47           const_4    local_7,0x4
        50037364 28 13           goto       LAB_5003738a
        50037366 13              ??         13h
        50037367 02              ??         02h
        50037368 31              ??         31h    1
        50037369 00              ??         00h
                             CatchHandlers::Ljava/lang/Error;
                             CatchHandlers::J
                             CatchHandlers::Ljava/lang/Exception;
        5003736a 13 02 31 00     const_16   v2,0x31
        5003736e 12 03           const_4    v3,0x0
        50037370 12 34           const_4    v4,0x3
        50037372 12 25           const_4    v5,0x2
        50037374 12 16           const_4    v6,0x1
        50037376 12 47           const_4    v7,0x4
        50037378 29 00 ed 01     goto_16    LAB_50037752
```



smali 코드 상에서 자세히 살펴보면 다음과 같았음. 예외가 발생하면, catch_0부터 시작하는 또 다른 flow가 존재하는 것을 확인할 수 있었음.

```java
.method public onClick(Landroid/view/View;)V
    .locals 18
    .param p1, "v"    # Landroid/view/View;

    move-object/from16 v1, p0
    .line 42
    iget-object v2, v1, Lcom/google/ctf/sandbox/o$1;->this$0:Lcom/google/ctf/sandbox/o;
    const/4 v3, 0x0
    iput v3, v2, Lcom/google/ctf/sandbox/o;->o:I
    const/16 v2, 0x31
    const/4 v3, 0x0
    const/4 v4, 0x3
    const/4 v5, 0x2
    const/4 v6, 0x1
    const/4 v7, 0x4
    goto :goto_0

    const/16 v2, 0x31

    :catch_0
    const/16 v2, 0x31
    const/4 v3, 0x0
    const/4 v4, 0x3
    const/4 v5, 0x2
    const/4 v6, 0x1
    const/4 v7, 0x4
    goto/16 :goto_3
        
    ...
        

    :goto_3
    :try_start_1
    iget-object v3, v1, Lcom/google/ctf/sandbox/o$1;->val$editText:Landroid/widget/EditText;
    invoke-virtual {v3}, Landroid/widget/EditText;->getText()Landroid/text/Editable;
    move-result-object v3
    invoke-virtual {v3}, Ljava/lang/Object;->toString()Ljava/lang/String;
    move-result-object v3
    .line 61
    .local v3, "flagString":Ljava/lang/String;
    invoke-virtual {v3}, Ljava/lang/String;->length()I
    move-result v5
    const/16 v6, 0x30
    if-eq v5, v6, :cond_2
    .line 62
    iget-object v4, v1, Lcom/google/ctf/sandbox/o$1;->val$textView:Landroid/widget/TextView;
```



ghidra로 해당 부분을 다시 살펴보니, 아예 다른 함수로 해석하여 보여주는 것을 확인할 수 있었음. 다음 동작을 요약하자면, 사용자가 입력한 string을 가져와서 0x30과 길이를 비교하고, string을 4byte 배열로 변경한 뒤 R.o 함수에 인자로 집어넣어 연산한 결과 값과 기존 존재하던 class 배열과 비교함. class에 대해서는 뒤에서 설명하겠음.

```java
void UndefinedFunction_5003736a(void)

{
  long lVar1;
  char cVar2;
  Editable ref;
  String ref_00;
  int iVar3;
  int iVar4;
  int unaff_v1;
  EditText ref_01;
  TextView ref_02;
  long[] plVar5;
  RuntimeException ref_03;
  o poVar6;
  
  ref_01 = unaff_v1.val$editText;
  ref = ref_01.getText();
  ref_00 = ref.toString();
  iVar3 = ref_00.length();
  if (iVar3 != 0x30) {
    ref_02 = unaff_v1.val$textView;
    ref_02.setText("❌");
    return;
  }
  iVar3 = 0;
  while (iVar4 = ref_00.length(), iVar3 < iVar4 / 4) {
    plVar5 = unaff_v1.this$0.o;
    cVar2 = ref_00.charAt(iVar3 * 4 + 3);
    plVar5[iVar3] = (long)((int)cVar2 << 0x18);
    plVar5 = unaff_v1.this$0.o;
    lVar1 = plVar5[iVar3];
    cVar2 = ref_00.charAt(iVar3 * 4 + 2);
    plVar5[iVar3] = lVar1 | (int)cVar2 << 0x10;
    plVar5 = unaff_v1.this$0.o;
    lVar1 = plVar5[iVar3];
    cVar2 = ref_00.charAt(iVar3 * 4 + 1);
    plVar5[iVar3] = lVar1 | (int)cVar2 << 8;
    plVar5 = unaff_v1.this$0.o;
    lVar1 = plVar5[iVar3];
    cVar2 = ref_00.charAt(iVar3 * 4);
    plVar5[iVar3] = lVar1 | (int)cVar2;
    iVar3 = iVar3 + 1;
  }
  plVar5 = R.o(unaff_v1.this$0.o[unaff_v1.this$0.o],0x100000000);
  if ((plVar5[0] % 0x100000000 + 0x100000000) % 0x100000000 !=
      unaff_v1.this$0.class[unaff_v1.this$0.o]) {
    ref_02 = unaff_v1.val$textView;
    ref_02.setText("❌");
    return;
  }
  poVar6 = unaff_v1.this$0;
  poVar6.o = poVar6.o + 1;
  if (unaff_v1.this$0.o.length <= unaff_v1.this$0.o) {
    ref_02 = unaff_v1.val$textView;
    ref_02.setText("🚩");
    return;
  }
  ref_03 = new RuntimeException();
  throwException(ref_03);
  return;
}
```



위의 예외 처리 구문으로 넘어가게 되는 과정은 다음과 같음.

우선 앞서 처음으로 디컴파일된 onClick 구문의 동작이 정상적으로 이루어지다가, 다음의 while 구문에서의 checkCast에서 Integer 형에 대하여 Character 형을 검사함으로써 Exception이 발생하게 됨. 이때부터 앞서 보았던 :catch_0 부터 구문이 시작됨.

```java
  pIVar3 = Integer.valueOf(0x3f);
  ppOVar5[0x30] = pIVar3;
  ref_01 = new StringBuilder();
  iVar6 = 0
  while (iVar6 < ppOVar5.length) {
    ref_04 = ppOVar5[iVar6];
    checkCast(ref_04,Character);
    cVar2 = ref_04.charValue();
    ref_01.append(cVar2);
    iVar6 = iVar6 + 1;
  }
```



또한 처음 시작되었을 때, smali에서는 `com/google/ctf/sandbox/o;->o:I`, 위의 디컴파일된 코드에서는 `unaff_v1.this$0.o` 가 나타내는 것은 index라고 볼 수 있음. 0x30 개의 문자를 4byte로 나누어 사이즈가 12인 배열을 사용하는데, 이 때 이 배열에서 사용하는 index임. 0부터 시작하여 다음의 코드에서 1씩 증가함.

```java
  poVar6 = unaff_v1.this$0;
  poVar6.o = poVar6.o + 1;
```

다음의 코드는 제대로된 분기 지점을 나타내는 코드로서 매우 중요한데, 이때 조건 문에서 이 index를 12와 비교하는 것을 확인할 수 있음.

```java
  if (unaff_v1.this$0.o.length <= unaff_v1.this$0.o) {
    ref_02 = unaff_v1.val$textView;
    ref_02.setText("🚩");
    return;
  }
```

사실 처음 이걸 봤을 때, 반복문이 아니여서 의문이 들었는데, 다음의 코드에서 예외를 발생시키므로 앞서 checkCast 예외가 발생했던 것처럼 다시  :catch_0 로 돌아가게 된다. 정리하자면 예외를 이용하여 goto를 구현한 것으로 보면 될 것 같다.

```java
  ref_03 = new RuntimeException();
  throwException(ref_03);
```



사용자가 입력한 값을 특정 연산하는 부분은 다음과 같다. 재귀로 구현되어 있어 복잡해 보이지만, 이는 Extended Euclidean algorithm을 이용하여 a와 b의 역원을 구하는 함수이다. a와 b를 입력하면 각각의 역원을 배열의 형태로 리턴한다.

```java
    public static long[] o(long a, long b) {
        if (a == 0) {
            return new long[]{0, 1};
        }
        long[] r = o(b % a, a);
        return new long[]{r[1] - ((b / a) * r[0]), r[0]};
    }
```

다음과 같이 사용하므로, 이는 0x100000000에 대하여 `this$0.o[index]`의 역원을 구하여 `this$0.class[index]`와 동일한지 비교한다고 볼 수 있다.

```java
  plVar5 = R.o(unaff_v1.this$0.o[unaff_v1.this$0.o],0x100000000);
  if ((plVar5[0] % 0x100000000 + 0x100000000) % 0x100000000 !=
      unaff_v1.this$0.class[unaff_v1.this$0.o]) {
    ref_02 = unaff_v1.val$textView;
    ref_02.setText("❌");
    return;
  }
```



연산된 결과와 비교하는 값은 com.ctf.sandbox.o::init()에서 초기화하는 것을 볼 수 있다. :array_0의 배열과 비교한다.

```java
# direct methods
.method public constructor <init>()V
    .locals 14

    .line 11
    invoke-direct {p0}, Landroid/app/Activity;-><init>()V

    :catch_0
    :try_start_0
    const/16 v0, 0xc

    new-array v1, v0, [J

    fill-array-data v1, :array_0

    iput-object v1, p0, Lcom/google/ctf/sandbox/o;->class:[J

    .line 16
    new-array v0, v0, [J

    iput-object v0, p0, Lcom/google/ctf/sandbox/o;->o:[J

    .line 17
    const/4 v0, 0x0

    iput v0, p0, Lcom/google/ctf/sandbox/o;->o:I
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0
    .catch Ljava/lang/Error; {:try_start_0 .. :try_end_0} :catch_0
    .catch I {:try_start_0 .. :try_end_0} :catch_1

    goto/16 :goto_0

    :try_start_1
    const/16 v0, 0xc

    :catch_1
    :goto_0
    return-void

    :array_0
    .array-data 8
        0x271986b
        0xa64239c9L
        0x271ded4b
        0x1186143
        0xc0fa229fL
        0x690e10bf
        0x28dca257
        0x16c699d1
        0x55a56ffd
        0x7eb870a1
        0xc5c9799fL
        0x2f838e65
    .end array-data
    :try_end_1
    .catch Ljava/lang/Exception; {:try_start_1 .. :try_end_1} :catch_0
.end method
```



## Solution

결과적으로 위 문제를 해결하기 위해서는 기존 존재하는 class 배열의 값으로 원래의 플래그를 찾아내야 한다.

a와 a^-1은 서로가 역원 관계이므로, 위의 R.o 함수는 역이 성립한다. 따라서 해당 동일한 함수를 이용하여 역으로 계산하면 플래그를 구할 수 있다.

```python
#/usr/bin/python3

def o(a, b) :
    if (a == 0) :
        return [0, 1];

    r = o(b % a, a);
    return [(r[1] - (((b // a) * r[0]))), r[0]]

def int2str(a):
    res = ''
    for i in range(0, 4):
        res += (chr((a >> (8*i)) & 0xff))
    return res

ans = [0x271986B, 0xA64239C9, 0x271DED4B, 0x1186143, 0xC0FA229F, 0x690E10BF, 0x28DCA257, 0x16C699D1, 0x55A56FFD, 0x7EB870A1, 0xC5C9799F, 0x2F838E65]

res = []
for i in ans:
    res.append(int2str(o(i, 0x100000000)[0]))

print('FLAG is ' + ''.join(res))
#FLAG is CTF{y0u_c4n_k3ep_y0u?_m4gic_1_h4Ue_laser_b3ams!}
```



## Reference

- http://pallergabor.uw.hu/androidblog/dalvik_opcodes.html
- https://github.com/luker983/google-ctf-2020/tree/master/reversing/android