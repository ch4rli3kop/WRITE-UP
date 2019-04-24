# [wargame.kr] flee button writeup



##### 문제

```shell
click the button!

i can't catch it!
```



문제를 살펴보면 다음 그림과 같다.



마우스 포인터위치 기준으로 `click  me!`가 움직이기 때문에, 해당 element에 clink 이벤트가 발생했을 경우, 발생하는 사건을 찾아서 직접 불러주도록 한다.

view-source로 보면 난독화가 걸려있는데, 디버깅 창으로 보면 난독화가 해제되어 있는 소스를 볼 수 있다.

`click me!`에 click 이벤트가 발생했을 때, 경로에 `?key=97c8'이 추가되므로 해당 경로를 넣어주면 flag를 얻을 수 있다.