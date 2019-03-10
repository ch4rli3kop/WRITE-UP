import re

fp = open('data', 'r')
data = fp.read()

pattern = '[a-z][A-Z]{3}[a-z][A-Z]{3}[a-z]'
r = re.compile(pattern)
result = ''
for i in r.findall(data):
    result += i[4]

print result
