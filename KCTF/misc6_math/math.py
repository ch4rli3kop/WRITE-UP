import random
import sys


print("This stage is the Math coding test!!")
print("If you solve the problem of 100 stages, you can get the flag!!")
print("Then, Work hard!\n")

operations = ['+','-','*','%']


count = 0
while True:
	x1 = random.randint(1, 7777)
	x2 = random.randint(1, 7777)
	x3 = random.randint(1, 7777)
	x4 = random.randint(1, 7777)
	x5 = random.randint(1, 7777)
	x6 = random.randint(1, 7777)
	x7 = random.randint(1, 7777)
	x8 = random.randint(1, 7777)
	x9 = random.randint(1, 7777)
	xa = random.randint(1, 7777)
	xb = random.randint(1, 7777)
	xc = random.randint(1, 7777)
	xd = random.randint(1, 7777)
	xe = random.randint(1, 7777)
	xf = random.randint(1, 7777)
	x10 = random.randint(1, 7777)

	op_seed = random.randint(0,3)

	Random_Quest = str(x1)+str(operations[op_seed])
	op_seed = random.randint(0,3)
	Random_Quest += str(x2)+str(operations[op_seed])
	op_seed = random.randint(0,3)
	Random_Quest += str(x3)+str(operations[op_seed])
	op_seed = random.randint(0,3)
	Random_Quest += str(x4)+str(operations[op_seed])
	op_seed = random.randint(0,3)
	Random_Quest += str(x5)+str(operations[op_seed])
	op_seed = random.randint(0,3)
	Random_Quest += str(x6)+str(operations[op_seed])
	op_seed = random.randint(0,3)
	Random_Quest += str(x7)+str(operations[op_seed])
	op_seed = random.randint(0,3)
	Random_Quest += str(x8)+str(operations[op_seed])
	op_seed = random.randint(0,3)
	Random_Quest += str(x9)+str(operations[op_seed])
	op_seed = random.randint(0,3)
	Random_Quest += str(xa)+str(operations[op_seed])
	op_seed = random.randint(0,3)
	Random_Quest += str(xb)+str(operations[op_seed])
	op_seed = random.randint(0,3)
	Random_Quest += str(xc)+str(operations[op_seed])
	op_seed = random.randint(0,3)
	Random_Quest += str(xd)+str(operations[op_seed])
	op_seed = random.randint(0,3)
	Random_Quest += str(xe)+str(operations[op_seed])
	op_seed = random.randint(0,3)
	Random_Quest += str(xf)+str(operations[op_seed])
	op_seed = random.randint(0,3)
	Random_Quest += str(x10)

	print(Random_Quest + "=???")
	#print eval(Random_Quest)
	answer = int(input("> "))

	if answer == eval(Random_Quest):
		print("OK right answer!\n")
		count += 1
	else:
		print("Sorry, that's not an answer!\n")

	if count == 100:
		print("COngratulation!!! you won!")
		with open("flag.txt",'r') as fp:
			print(fp.read())
		sys.exit()
