import string

upperString = string.ascii_uppercase
lowerString = string.ascii_lowercase

fp = open('data', 'r')
data = fp.read()
result = ''

for i in range(0, len(data)-9):
        if data[i] in lowerString and data[i+4] in lowerString and data[i+8] in lowerString:
            c = [j for j in (data[i+1:i+4] + data[i+5:i+8]) if j in upperString]
            if len(c) == 6:
                result += data[i+4]

print result
