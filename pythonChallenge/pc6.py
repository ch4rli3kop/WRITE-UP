#!/usr/bin/python3
import urllib.request, re, zipfile, io

data = urllib.request.urlopen('http://www.pythonchallenge.com/pc/def/channel.zip').read()
zfile = io.BytesIO()
zfile.write(data)
z = zipfile.ZipFile(zfile, 'r')

r = re.compile(r'Next nothing is (\d+)')
nothing = '90052'

result = ''
while True:
    data = z.read(nothing + '.txt').decode('utf-8')
    print(data)
    result += z.getinfo(nothing + '.txt').comment.decode('utf-8')
    if r.match(data):
        nothing = data.split(' ')[-1]
    else:
        break
print(result)
