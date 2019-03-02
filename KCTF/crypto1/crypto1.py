from pwn import *
import random
import collections

context.log_level='debug'

p = remote("ctf.kuality.kr", 12358)

Table1={'0':'var','1':'var','2':'var','3':'var','4':'var','5':'var','6':'var','7':'var','8':'var','9':'var','a':'var','b':'var','c':'var','d':'var','e':'var','f':'var','g':'var','h':'var','i':'var','j':'var','k':'var','l':'var','m':'var','n':'var','o':'var','p':'var','q':'var','r':'var','s':'var','t':'var','u':'var','v':'var','w':'var','x':'var','y':'var','z':'var','A':'var','B':'var','C':'var','D':'var','E':'var','F':'var','G':'var','H':'var','I':'var','J':'var','K':'var','L':'var','M':'var','N':'var','O':'var','P':'var','Q':'var','R':'var','S':'var','T':'var','U':'var','V':'var','W':'var','X':'var','Y':'var','Z':'var',' ':'var','!':'var','@':'var',"#":'var','$':'var','%':'var','^':'var','&':'var','*':'var','(':'var',')':'var','{':'var','}':'var','_':'var','+':'var','-':'var',':':'var','~':'var'}
Table = collections.OrderedDict(sorted(Table1.items()))

p.recvuntil("Seed : ")
a = p.recvline()
a = a[:-1]

print("seed : "+a)
print("Table.key")
print(Table.keys())

aa = float(a)
print(aa)
random.seed(aa)
value = random.sample(range(0,len(Table)),len(Table))

for i,j in zip(Table.keys(),range(0,len(Table))):
    Table[i]=value[j]

print("value")
print(value)

print("Table.key")
print(Table.keys())

print("Table")
print(Table)

p.recvuntil(")])\n")
string = p.recv(100)

# listring = list(string)

# for i in range(0, len(listring)):
#    listring[i] = ord(listring[i])

# print(listring)

# for i in range(0, len(listring)):
#    	for j in Table.keys():
#    		#print(type(listring[i]))
#    		if Table[j]==listring[i]:
#    			print j

listc = list(string)
res = OrderedDict((v,k) for k,v in Table.items())
print(Table)
print(res)
p=""
for i in listc:
    p+=res[ord(i)]
print(p)