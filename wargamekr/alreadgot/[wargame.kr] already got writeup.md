# [wargame.kr] already got writeup

##### 문제

```shell
can you see HTTP Response header?
```



해당 사이트에 접속하면 받을 수 있는 http response를 까보면 flag를 얻을 수 있다.

```http
HTTP/1.1 200 OK
Date: Sat, 20 Apr 2019 07:43:41 GMT
Server: Apache/2.4.18 (Ubuntu)
FLAG: 697037b1f9558d29bca1b70054cf083d36a656b5
Content-Length: 27
Keep-Alive: timeout=5, max=100
Connection: Keep-Alive
Content-Type: text/html; charset=UTF-8

you've already got key! :p

```

