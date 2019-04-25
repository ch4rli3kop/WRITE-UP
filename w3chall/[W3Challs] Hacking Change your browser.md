# [W3Challs] Hacking Change your browser



```php
 
<!DOCTYPE HTML>
<html>
<head>
	<title>Hacking Challenge N&deg;1 - W3Challs</title>
	<meta name="owner" content="W3Challs" />
	<meta name="publisher" content="w3challs" />
	<meta name="copyright" content="w3challs" />
	<meta name="robots" content="noindex,nofollow">
	<meta http-equiv="Content-language" content="en" />
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
</head>
<body>

<p align="center">To solve this challenge, your browser must be: <strong>W3Challs_browser</strong></p>
<p style="border: 1px dotted; border-color: red; color: red; text-align: center;">Your current browser is <strong>Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0</strong></p>

</body>
</html>
```

browser 정보를 W3Challs_browser로 변경하면 될 것 같다.

fiddler의 composer 기능을 활용해서 User-Agent를 W3Challs_browser로 바꿔서 request를 보내면 다음과 같은 결과를 얻을 수 있다.

```http
HTTP/1.1 200 OK
Date: Wed, 24 Apr 2019 23:52:50 GMT
Server: Apache
Content-Type: text/html; charset=UTF-8
Keep-Alive: timeout=15, max=100
Connection: Keep-Alive
Content-Length: 636

 
<!DOCTYPE HTML>
<html>
<head>
	<title>Hacking Challenge N&deg;1 - W3Challs</title>
	<meta name="owner" content="W3Challs" />
	<meta name="publisher" content="w3challs" />
	<meta name="copyright" content="w3challs" />
	<meta name="robots" content="noindex,nofollow">
	<meta http-equiv="Content-language" content="en" />
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
</head>
<body>

<p align="center">Well done ! You solved this challenge, the password to validate it is the acronym of "<strong>SQL</strong>"</p>
	<p align="center">( Everything lowercase with spaces between each word )</p>

</body>
</html>
```

password는 `structured query language`이다.

