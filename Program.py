import sys
import random
import math
from pulp import *
import time

LinearProblem = LpProblem ("Patrol", LpMaximize)

modular=0
consToThis = 1
oldstuff = 0.5

numAtt = 1
listAtt = [1 for x in range (numAtt)]
numVerAtt = [1 for x in range (numAtt)]

listAtt[0] = 3
numVerAtt[0] = 5

maxLen = 0
numVer = 0

for i in range (numAtt):
	numVer += numVerAtt[i]

#Problem:
#[x][0] - length
#[x][1] - succ for def 
#[x][2] - fail for def 
#[x][3] - succ for att
#[x][4] - fail for att
Problem = [[1 for x in range(5)] for x in range(numVer)]
for i in range (numVer):
	Problem[i][2] = 0
	Problem[i][4] = 0

first = 0
for i in range (numAtt):
	for j in range (first, first+numVerAtt[i]):
		Problem[j][0] = listAtt[i]+1
	if maxLen <= listAtt[i]:
		maxLen = listAtt[i]+1
	first += numVerAtt[i]

def gcd(a,b):
	if a>b:
		c = a
		a = b
		b = c
	while (a):
		c = a
		a = b % a
		b = c
	return b

def lcm(a,b):
	return (a*b)/gcd(a,b)

if modular==1:
	numAver = listAtt[0]
	for i in range (1, numAtt):
		numAver = lcm(numAver, listAtt[i])
	numAver = int(numAver)
	
else:
	numAver=1
	
IsActive = [[1 for x in range(numAver)] for y in range(numVer)]
AQueue = [[0 for x in range(2)] for y in range(numAver*numVer)]
Edge = [[0 for x in range(numVer)] for y in range(numAver)]

WhereItIs = [[[-1 for z in range (2)] for x in range(numAver)] for y in range(numVer)] 

Queue = [[[0 for x in range(3)] for z in range(2)] for y in range(numAver*numVer)]
numQueue = [0 for x in range(2)]	

PathToQueue = [[[0 for x in range(maxLen)] for z in range(2)] for y in range(numAver*numVer)]

def fillEdgesModular ():
	for i in range (numVer):
		for j in range (numAver):
			Edge[j][i] = (j+1)%numAver
			

ConsMatrix = [[[0 for x in range(numVer)] for y in range(numAver)] for z in range (numVer)]
OriginalMatrix = [[[0 for x in range(numVer)] for y in range(numAver)] for z in range (numVer)]
RandNumbers = [0 for x in range(numVer)]

MatrixName = [[["a" for x in range(numVer)] for y in range(numAver)] for z in range (numVer)]
ResultName = [[["a" for x in range(numVer)] for y in range(numAver)] for z in range (numVer)]

ProbHereInK = [[[[[[0 for a in range(maxLen)] for b in range (numAver)] for c in range(numVer)] for d in range(numVer)] for e in range(numAver)] for f in range(numVer)]

for i in range (numVer):
	for j in range (numAver):
		for k in range (numVer):
			MatrixName[i][j][k] = "Matrix["+str(i)+"]["+str(j)+"]["+str(k)+"]"
			
for i in range (numVer):
	for j in range (numAver):
		for k in range (numVer):
			ResultName[i][j][k] = "Result["+str(i)+"]["+str(j)+"]["+str(k)+"]"
		
Matrix = [[[LpVariable(MatrixName[z][y][x], 0, 1) for x in range(numVer)] for y in range(numAver)] for z in range(numVer)]
Result = [[[LpVariable(ResultName[z][y][x], 0, 1) for x in range(numVer)] for y in range(numAver)] for z in range(numVer)]

worst = LpVariable("Worst situation imaginable", 0, 1)

Result = [0.0 for x in range(numVer)]
ProbIn = [[[0.0 for z in range (2)] for x in range(numAver)] for y in range(numVer)]
NewProbIn = [[[0.0 for z in range (2)] for x in range(numAver)] for y in range(numVer)]
Constants = [[0 for x in range(4)] for y in range(10000)] 


def fillConsMatrixRand ():
	sumTo1 = 0
	for i in range (numVer):
		for k in range (numAver):
			for j in range (numVer):
				RandNumbers[j] = random.random()
				sumTo1 += RandNumbers[j]
			for j in range (numVer):
				ConsMatrix[i][k][j] = RandNumbers[j]/sumTo1
				ConsMatrix[i][k][j] = ConsMatrix[i][k][j]*consToThis
			sumTo1 = 0
			
#TOHLE BUDU HODNE MENIT
def makeProblem ():
	global LinearProblem
	for start in range(numVer):
		for auto in range(numAver):
			for end in range(numVer):
				LinearProblem += 0 <= Matrix[start][auto][end]
			#LinearProblem += 0.01 == Matrix[start][auto][2]
			if IsActive[start][auto]==0:
				continue
			LinearProblem += sum(Matrix[start][auto][end] for end in range(numVer)) == 1
			for end in range(numVer):
				if start==end:
					continue
				LinearProblem += worst <= Problem[end][1]*sum(sum(Matrix[last][lastAuto][end]*sum(ProbHereInK[start][auto][end][last][lastAuto][k] for k in range(Problem[end][0]-1)) for last in range(numVer)) for lastAuto in range(numAver))

def fillProbHereInK ():
	for end in range (numVer):
		for startAuto in range (numAver):
			for start in range (numVer):
				if start==end:
					continue
				if IsActive[start][startAuto]==0:
					continue
				ProbHereInK[start][startAuto][end][start][startAuto][0]=1.0
				#print ("Attack on", end, "starting in", start, startAuto)
				numCons = 0
				numQueue[0] = 1
				Queue[0][0][0] = start
				Queue[0][0][1] = startAuto
				Queue[0][0][2] = 1.0
				numQueue[1] = 0
				s = 0
				for step in range (Problem[end][0]-1):
					for l in range (numQueue[s]):
						i = Queue[l][s][0]
						k = Queue[l][s][1]
						WhereItIs[i][k][s] = -1
						for j in range (numVer):
							if j==end:
								continue
						
							if (ConsMatrix[i][k][j]>0):
								#ProbHereInK[start][startAuto][end][j][Edge[k][j]][step+1]+=Queue[l][s][2]*ConsMatrix[i][k][j]
								if (WhereItIs[j][Edge[k][j]][1-s]>-1):
									#print ("It's here.")
									w = WhereItIs[j][Edge[k][j]][1-s]
									Queue[w][1-s][2] += Queue[l][s][2]*ConsMatrix[i][k][j]
									if (step==0 and i==0 and k==0 and end==1 and j==2):
										print ("Picovinyyyyy")
										print (Queue[l][s][2])
										print (ConsMatrix[i][k][j])
										print ()
								else:
									#print ("It's new.")
									Queue[numQueue[1-s]][1-s][0] = j
									Queue[numQueue[1-s]][1-s][1] = Edge[k][j]
									Queue[numQueue[1-s]][1-s][2] = Queue[l][s][2]*ConsMatrix[i][k][j]
									WhereItIs[j][Edge[k][j]][1-s] = numQueue[1-s]
									numQueue[1-s] += 1
							Queue[l][s][2] = 0
					for last in range (numVer):
						if last==end:
							continue
						for lastAuto in range (numAver):
							if WhereItIs[last][lastAuto][1-s]!=-1:
								w = WhereItIs[last][lastAuto][1-s]
								#ProbHereInK[start][startAuto][end][last][lastAuto][step+1] = Queue[w][1-s][2]
					numQueue[s] = 0
					s = 1-s
				
				for l in range (numQueue[s]):
					WhereItIs[i][k][s] = -1
	return 0;

def nullProbHereInK ():
	for start in range(numVer):
		for auto in range(numAver):
			for end in range(numVer):
				for last in range(numVer):
					#if last==end:
						#continue
					for lastAuto in range(numAver):
						for k in range(Problem[end][0]):
							#if (start==0 and auto==0 and end==1):
								#print (ProbHereInK[start][auto][end][last][lastAuto][k])
								#if k==Problem[end][0]-1:
									#print ()
							ProbHereInK[start][auto][end][last][lastAuto][k] = 0
	
	
def printConsMatrix ():
	for i in range (numVer):
		for j in range (numAver):
			for k in range (numVer):
				print (ConsMatrix[i][j][k], end=" ")
			print ("")
		print ("")
	return 0; 

def printMatrix ():
	for i in range (numVer):
		for j in range (numAver):
			for k in range (numVer):
				print (Matrix[i][j][k].value(), end=" ")
			print ("")
		print ("")
	return 0; 

#TO SE TAKY ASI ZMENI
def CalculateResult ():
	worstres = 0.0
	bestres = -1.0
	for end in range (numVer):
		for startAuto in range (numAver):
			for start in range (numVer):
				if start==end:
					continue
				if IsActive[start][startAuto]==0:
					continue
				probofdef = 0.0
				numQueue[0] = 1
				Queue[0][0][0] = start
				Queue[0][0][1] = startAuto
				Queue[0][0][2] = 1.0
				numQueue[1] = 0
				s = 0
				for step in range (Problem[end][0]-1):
					#if numQueue[s]==0:
						#print (numQueue[1-s])
						#print ("WTF")
						#time.sleep(2)
					#time.sleep(3)
					#print ("New Step")
					for l in range (numQueue[s]):
						i = Queue[l][s][0]
						k = Queue[l][s][1]
						WhereItIs[i][k][s] = -1
						#print (l, ":", i, k, Queue[l][s][2])
						#time.sleep(2)
						for j in range (numVer):
							if j==end:
								probofdef += Queue[l][s][2]*Matrix[i][k][j].value()
							else:
								if (ConsMatrix[i][k][j]>0):
									if (WhereItIs[j][Edge[k][j]][1-s]>-1):
										#print ("It's here.")
										w = WhereItIs[j][Edge[k][j]][1-s]
										Queue[w][1-s][2] += Queue[l][s][2]*Matrix[i][k][j].value()
									else:
										#print ("It's new.")
										Queue[numQueue[1-s]][1-s][0] = j
										Queue[numQueue[1-s]][1-s][1] = Edge[k][j]
										Queue[numQueue[1-s]][1-s][2] = Queue[l][s][2]*Matrix[i][k][j].value()
										WhereItIs[j][Edge[k][j]][1-s] = numQueue[1-s]
										numQueue[1-s] += 1
					numQueue[s] = 0
					s = 1-s
				for l in range (numQueue[s]):
					i = Queue[l][s][0]
					k = Queue[l][s][1]
					WhereItIs[i][k][s] = -1
				nowresatt = probofdef*Problem[end][4]+(1-probofdef)*Problem[end][3]
				nowresdef = probofdef*Problem[end][1]+(1-probofdef)*Problem[end][2]
				if nowresatt>bestres:
					bestres = nowresatt
					worstres = nowresdef
				else: 
					if nowresatt==bestres:
						worstres = min({worstres, nowresdef})
	return worstres;

def CalculatedToCons (better):
	for i in range (numVer):
		for j in range (numAver):
			for k in range (numVer):
				if better==1:
					new = ConsMatrix[i][j][k]*oldstuff+Matrix[i][j][k].value()*(1-oldstuff)
				else:
					new = ConsMatrix[i][j][k]*oldstuff+(2*ConsMatrix[i][j][k]-Matrix[i][j][k].value())*(1-oldstuff)
				#if new != ConsMatrix:
					#print ("No toto!")
				ConsMatrix[i][j][k] = new*consToThis

#TROCHU NECHAPU
def addConstrain (first, num, length):
	global LinearProblem
	while ((num%length)>0):
		num -= 1
	for i in range (numVer):
		for j in range (numAver):
			for k in range (first, first+num):
				if ((k+j)%length==0):
					continue
				LinearProblem += Matrix[i][j][k] == 0
				ConsMatrix[i][j][k] = 0

#TROCHU NECHAPU
def addThemAll (attacks):
	first = 0
	for i in range (attacks):
		addConstrain(first, numVerAtt[i], listAtt[i])
		first += numVerAtt[i]

#TROCHU NECHAPU
def addConsConstrain (first, num, length):
	oldnum = num
	while ((num%length)>0):
		num -= 1
	for i in range (numVer):
		for j in range (numAver):
			for k in range (first, first+num):
				if ((k+j)%length==0):
					continue
				ConsMatrix[i][j][k] = 0
				IsActive[k][(j+1)%numAver] = 0
			#for k in range (first+num, first+oldnum):
				#ConsMatrix[i][j][k] = 0

def init(attacks):
	for i in range (numVer):
		for k in range (numAver):
			for j in range (numVer):
				ConsMatrix[i][k][j] = 1
	first = 0
	for i in range (attacks):
		addConsConstrain(first, numVerAtt[i], listAtt[i])
		first += numVerAtt[i]
		
	for i in range (numVer):
		for k in range (numAver):
			sum = 0
			for j in range (numVer):
				sum += ConsMatrix[i][k][j]
			for j in range (numVer):
				ConsMatrix[i][k][j] /= sum
				
def printProbHereInK():
	for i in range(numVer):
		for j in range(numVer):
			for k in range (Problem[j][0]):
				for l in range (numVer):
					print (i, end=" ")
					print (j, end=" ")
					print (k, end=" ")
					print (l, end=" ")
					print (ProbHereInK[i][0][j][l][0][k])
	
newres = 0
oldres = 0
fillEdgesModular()
if modular==1:
	init(numAtt)
else:
	fillConsMatrixRand()
#printConsMatrix()
for i in range (numVer):
	for j in range (numAver):
		for k in range (numVer):
			OriginalMatrix[i][j][k] = ConsMatrix[i][j][k]
for i in range (20):
	LinearProblem = LpProblem ("Patrol", LpMaximize)
	LinearProblem += worst
	print ("Making problem...")
	if modular==1:
		addThemAll(numAtt)
		#sameConstrain()
	fillProbHereInK()
	makeProblem()
	print ("Solving...")
	LinearProblem.solve()
	print ("Solved!")
	#printMatrix()
	#printConsMatrix()
	#print (LpStatus[LinearProblem.status])
	print (value(LinearProblem.objective))
	newres = CalculateResult()
	print (newres)
	print (newres-oldres)
	print ()
	if (newres-0.0001<oldres and newres>oldres):
		break
	if (i==19):
		break
	CalculatedToCons(1)
	oldres = newres
	nullProbHereInK()
printProbHereInK()
printMatrix ()
	
#ProbHereInK = [[[[[[0 for a in range(maxLen)] for b in range (numAver)] for c in range(numVer)] for d in range(numVer)] for e in range(numAver)] for f in range(numVer)]
