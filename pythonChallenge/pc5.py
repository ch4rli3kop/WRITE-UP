#!/usr/bin/python3
import urllib.request
import pickle

data = urllib.request.urlopen('http://www.pythonchallenge.com/pc/def/banner.p').read()
listedData = pickle.loads(data)
result = ''
for line in listedData:
    result += ''.join(k*v for k, v in line)
    result += '\n'
print(result)
