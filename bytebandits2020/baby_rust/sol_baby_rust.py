a = 'adhmp`badO|sL}JuvvFmiui{@IO}QQVRZ'
result = ''
for i in range(7, 0x21+7):
    result += chr(ord(a[i-7]) ^ i)
print(result)

