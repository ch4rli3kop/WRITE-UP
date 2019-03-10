#!/usr/bin/python3

import urllib.request
'''
nothing = '12345'
while True:
    res = urllib.request.urlopen('http://www.pythonchallenge.com/pc/def/linkedlist.php?nothing=%s'%nothing)
    data = res.read().decode('utf-8')
    if 'and the next nothing is' not in data:
        break
    nothing = data.split(' ')[-1]
    print(data)

print('final : %s'%nothing)
'''
nothing = '8022'
while True:
        res = urllib.request.urlopen('http://www.pythonchallenge.com/pc/def/linkedlist.php?nothing=%s'%nothing)
        data = res.read().decode('utf-8')
        if 'and the next nothing is' not in data:
            break
        nothing = data.split(' ')[-1]
        print(data)

print('final : %s'%data)
