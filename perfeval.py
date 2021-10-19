#import numpy as np
#import sys
movielength = 3500
times1 = [line.rstrip('\n') for line in open('client_logE', 'r')]
times=[0 for t1 in range(movielength + 2)]
t1=0
for t in range(len(times1)-8):
	times[t1] = (times1[t])
	t1=t1+1
fw = open('sk.txt', 'w')


'''
for t2 in range (0,3):
	print times[t2]
print "array len " + str(len(times))
'''


startTime = times[0]
endTime = times[len(times) - 1]
d = times[1:(len(times) - 1)] # d is of length 30002 - 1 - 1 = 30000
u = [round(float(d[i]) - float(d[i-1]), 3)*1000 for i in range(2, movielength)]
'''u[2:] = u[:]
u[0] = 0
u[1] = 0'''
#for time in range(len(d)):
#	if time >= 2:
#		u[time] = float(d[time]) - float(d[time - 1]) # u is of length 30000 - 1 = 29999
		#u[time] = float(d[time] - d[time - 1]) # u is of length 30000 - 1 = 29999

v = sorted(u, reverse=True) # v is same length as u

v[2:] = v[:]
v[0] = 0
v[1] = 0

vsum = [sum(v[2:k]) for k in range(2, len(v))]
sk = [0 for i in range(movielength)]
for k in range(2, len(vsum)):
	sk[k] = round(vsum[k] / (10 * (k - 1)),2)
for k in range(len(vsum)):
	#s = 'u[' + str(k) + '] = ' + str(u[k]) + '\n'
	#fw.write(s)
	#s = 'v[' + str(k) + '] = ' + str(v[k]) + '\n'
	#fw.write(s)
	#s = 'sk[' + str(k) + '] = ' + str(sk[k]) + '\n'
	s = str(sk[k])
	fw.write(s + '\n')
	
#for k in range(len(v)):
#	fw.write(str(v[k])+'\n')
fw.close()

#######################
#ScenarioF calculation
#######################
'''
movielength = 15000
times1 = [line.rstrip('\n') for line in open('client_logF', 'r')]
times=[0 for t1 in range(movielength + 2)]
t1=0
for t in range(len(times1)-8):
	times[t1] = (times1[t])
	t1=t1+1
fw = open('sk.txt', 'w')

startTime = times[0]
endTime = times[len(times) - 1]
d = times[1:(len(times) - 1)] # d is of length 30002 - 1 - 1 = 30000
u = [round(float(d[i]) - float(d[i-1]), 3)*1000 for i in range(2, movielength)]

v = sorted(u, reverse=True) # v is same length as u

v[2:] = v[:]
v[2] = 10
v = sorted(v, reverse=True)
v[0] = 0
v[1] = 0

vsum = [sum(v[2:k]) for k in range(2, len(v))]
sk = [0 for i in range(movielength)]
for k in range(2, len(vsum)):
	sk[k] = round(vsum[k] / (10 * (k - 1)),2)
for k in range(len(vsum)):
	#s = 'u[' + str(k) + '] = ' + str(u[k]) + '\n'
	#fw.write(s)
	#s = 'v[' + str(k) + '] = ' + str(v[k]) + '\n'
	#fw.write(s)
	#s = 'sk[' + str(k) + '] = ' + str(sk[k]) + '\n'
	s = str(sk[k])
	fw.write(s + '\n')

fw.close()
'''

#######################
#ordered 
#######################
'''
movielength = 15000
times1 = [line.rstrip('\n') for line in open('client_logA', 'r')]
times=[0 for t1 in range(movielength + 2)]
t1=0
for t in range(len(times1)-8):
	times[t1] = (times1[t])
	t1=t1+1
fw = open('sk.txt', 'w')

startTime = times[0]
endTime = times[len(times) - 1]
d = times[1:(len(times) - 1)] # d is of length 30002 - 1 - 1 = 30000
u = [round(float(d[i]) - float(d[i-1]), 3)*1000 for i in range(2, movielength)]

v = sorted(u, reverse=True) # v is same length as u

for k in range(len(v)):
	fw.write(str(v[k])+'\n')
fw.close()
'''

#######################
#unordered
#######################
'''
movielength = 15000
times1 = [line.rstrip('\n') for line in open('client_logA', 'r')]
times=[0 for t1 in range(movielength + 2)]
t1=0
for t in range(len(times1)-8):
	times[t1] = (times1[t])
	t1=t1+1
fw = open('sk.txt', 'w')


startTime = times[0]
endTime = times[len(times) - 1]
d = times[1:(len(times) - 1)] # d is of length 30002 - 1 - 1 = 30000
u = [round(float(d[i]) - float(d[i-1]), 3)*1000 for i in range(2, movielength)]

v=u

for k in range(len(v)):
	fw.write(str(v[k])+'\n')
fw.close()
'''
