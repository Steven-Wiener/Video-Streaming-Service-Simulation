import sys
from socket import *
from select import *
import time
import random
import math

# Set print destination for later log file
sys.stdout = open('client_log', 'w')

# ##################
# GLOBAL VARIABLES #
# ##################
# Constants
# Server and port setup
serverName1 = '10.10.1.2' #VM1
serverName2 = '10.10.2.2' #VM2
serverName3 = '10.10.3.1' #VM3
serverName4 = '10.10.4.2' #VM4
serverPort = 13000
serverAddr1 = (serverName1, serverPort)
serverAddr2 = (serverName2, serverPort)
serverAddr3 = (serverName3, serverPort)
serverAddr4 = (serverName4, serverPort)
s = socket(AF_INET, SOCK_DGRAM) # Create socket
# serverAddress = [serverAddr1,serverAddr2,serverAddr3,serverAddr4] 
# More constants
packetLength = 1029

movieLength = 30000

# Initial values changed by functions
serverAddr = serverAddr1
frameBuffer = [' ' for i in range(32)]
packet = ' '
frameNumber = 0
frameData = 0
#lastBufferFrame = False
frameDisplayed = 0 # Once this hits 30000 we're done
# Initial values not changed by functions
VM = 0
waiting = False
case1 = False
case2 = False
case3 = False
case4 = False
case5 = False
WINDOWSIZE = 8
initTimeToWait = 3.00 #8.00
timeoutInterval = 2
OOBFrame = 0
frameReqTime = [0 for i in range(movieLength)]
serverInstAvgRTT = [0 for i in range(4)] #need to be float array
serverAvgRTT = [0 for i in range(4)] #need to be float array
serverReqCount = [0 for i in range(4)]
serverRecvCount = [0 for i in range(4)]
serverRecvCountInst = [0 for i in range(4)]
serverTimeout = [0 for i in range(4)]
serverGoodList = [1 for i in range(4)] # All are good in beginning
serverReqThisCycle = [2 for i in range(4)] # All get 2 reqs in beginning
serverPerformance = [0 for i in range(4)]
serverPerformanceInst = [0 for i in range(4)]
packetReqTime = [0 for i in range(movieLength)]
packetRTT = [0 for i in range(movieLength)]
packetReqServer = [5 for i in range(movieLength)]
packetRecvServer = [0 for i in range(movieLength)]
packetsInFlight = [0 for i in range(4)]
packetsDroppedByServer = [0 for i in range(4)]
packetsToReq = [0 for i in range(10)]
roulette = [i for i in range(4)]
rewindComplete = False
pauseComplete = False

def mean(values):
	return sum(values) * 1.0 / len(values)

def std(values):
	length = len(values)
	m = mean(values)
	total_sum = 0
	for i in range(length):
		total_sum += ((values[i] - m) ** 2)
	under_root = total_sum * 1.0 / length
	return math.sqrt(under_root)

def rewind(frameChange):
	global frameDisplayed
	global frameBuffer
	frameDisplayed = frameChange
	frameBuffer = [0 for i in range(32)]
	packetReqTime = [0 for i in range(frameChange, movieLength)]
	packetReqServer = [5 for i in range(frameChange, movieLength)]
	init()
	#for i in range(16):
	#	requestPacket(i + frameChange, i % 4)
	#print "Reverse, reverse!: Buffering..."
	#print "Current Time: ", time.time()
	#Resume

def forward(frameChange):
	global frameDisplayed
	global frameBuffer
	frameDisplayed = frameChange
	frameBuffer = [0 for i in range(32)]
	packetReqTime = [0 for i in range(frameChange, movieLength)]
	packetReqServer = [5 for i in range(frameChange, movieLength)]
	init()
	#for i in range(16):
	#	requestPacket(i + frameChange, i % 4)
	#print "Forward: Buffering..."
	#print "Current Time: ", time.time()
	#Resume
	
def pause():
	global frameDisplayed
	waitTime = time.time() + 10
	packetReqTime = [0 for i in range(frameDisplayed + 32, movieLength)]
	packetReqServer = [5 for i in range(frameDisplayed + 32, movieLength)]
	#print "Current Time: ", time.time()
	while time.time() < waitTime:
		receivePacket()
	
def init():
	framestorequest = [0 for i in range(8)]
	
	requestPacket(str(frameDisplayed), 0)
	requestPacket(str(frameDisplayed + 1), 1)
	requestPacket(str(frameDisplayed + 2), 2)
	requestPacket(str(frameDisplayed + 3), 3)
	
	count = 0
	while (True):
		if receivePacket() == 1:
			if ((int(frameNumber) + 4) < frameDisplayed + 32):
				count = count + 1
				requestPacket(str(int(frameNumber) + 4), (count) % 4)
			if ((frameBuffer[31] != ' ') or (time.time() - startInitTime > 3.00)): 
				break
	
	while frameBuffer[0] == ' ':
		if ((time.time() - packetReqTime[frameDisplayed]) > .2):
			requestPacket(str(frameDisplayed), random.randrange(4))
		receivePacket()
	
	count = 0
	for frame in range(0, 32):
		if frameBuffer[frame] == ' ' and packetReqTime[frame] == 0:
			if count < 8:
				framestorequest[count] = frame
				count += 1
				if count == 8:
					break				
	while (count < 8):
		framestorequest[count] = frameDisplayed + 31 + 8 - count
		count = count + 1
	for count in range (0, 8):
		requestPacket(framestorequest[count], count % 4)

def requestPacket(frameNumber, VM):
	global serverAddr
	global packetsInFlight
	global packetsDroppedByServer
	global packetReqServer
	if (VM == 0):
		serverAddr = serverAddr1
	elif (VM == 1):
		serverAddr = serverAddr2
	elif (VM == 2):
		serverAddr = serverAddr3
	else:
		serverAddr = serverAddr4

	#print packetReqTime[int(frameNumber)]
	if packetReqServer[int(frameNumber)] != 5: # assume packet dropped by original server
		#packetsInFlight[packetReqServer[int(frameNumber)]] -= 1
		packetsDroppedByServer[packetReqServer[int(frameNumber)]] += 1
		#print "Packet Dropped: ", str(frameNumber).zfill(5), " by VM",;sys.stdout.softspace = False; print (packetReqServer[int(frameNumber)] + 1)
	packetReqTime[int(frameNumber)] = time.time()
	packetReqServer[int(frameNumber)] = VM
	serverReqCount[VM] += 1
	packetsInFlight[VM] += 1
	
	#print"Requesting F# ", str(frameNumber).zfill(5), " from VM",;sys.stdout.softspace = False; print (VM + 1)
	
	s.sendto(str(frameNumber).zfill(5), serverAddr)

def receivePacket():
	global frameNumber
	global frameData
	global packetsInFlight
	global packetRTT
	global packetRecvServer
	global serverRecvCount
	global serverAvgRTT
	
	readable, writeable, exception = select([s],[],[],0)
	if readable:
		#if not lastBufferFrame:
		packet, serverAddr = s.recvfrom(packetLength)
		frameNumber = packet[:5]
		frameData = packet[6:]
		
		if (serverAddr == serverAddr1):
			VM = 0
		elif (serverAddr == serverAddr2):
			VM = 1
		elif (serverAddr == serverAddr3):
			VM = 2
		elif (serverAddr == serverAddr4):
			VM = 3
		#print "Received from VM",;sys.stdout.softspace=False; print (VM + 1), ": F#", frameNumber
		#if packetRTT[int(frameNumber)] != 0:
			#print "Duplicate Packet Received:", frameNumber
			#packetsInFlight[VM] -= 1
		if int(frameNumber) > (frameDisplayed + 31):
			#print "Out of bounds of frameBuffer. packetReqTime set to 0"
			OOBFrame = int(frameNumber)
			OOBTime = time.time()
			packetReqTime[int(frameNumber)] = 0
			packetReqServer[int(frameNumber)] = 5
			packetRTT[int(frameNumber)] = 0
			packetsInFlight[VM] -= 1
		else:
			# Change this for Scenario E ***
			packetRTT[int(frameNumber)] = time.time() - packetReqTime[int(frameNumber)] #set to some max value if timeout happens
			packetRecvServer[int(frameNumber)] = VM
			packetsInFlight[VM] -= 1
			serverRecvCount[VM] += 1
			serverAvgRTT[VM] = ((serverAvgRTT[VM] * (serverRecvCount[VM] - 1)) / serverRecvCount[VM]) + (packetRTT[int(frameNumber)] / serverRecvCount[VM])
			if serverRecvCountInst[VM] < 15:
				serverRecvCountInst[VM] += 1
			serverInstAvgRTT[VM] = ((serverInstAvgRTT[VM] * (serverRecvCountInst[VM] - 1)) / serverRecvCountInst[VM]) + (packetRTT[int(frameNumber)] / serverRecvCountInst[VM])
			congestionFactor = 0.1 # CONSTANT, CAN CHANGE AFTER TWEAKING
			serverPerformanceInst[VM] = 1 / (serverInstAvgRTT[VM] + (packetsDroppedByServer[VM] * congestionFactor))
			
			# Put frame in frameBuffer
			if frameDisplayed <= int(frameNumber):
				frameBuffer[int(frameNumber) - frameDisplayed] = frameData
#				print "Adding to frameBuffer:", frameNumber
		return 1
	else:
		return 0
				
# ############
# MAIN START #
# ############
# Send four requests for first four frames (one from each server)
startInitTime = time.time()
OOBTime = time.time()
init()

# These are used to keep track of how long each frame should play and how long the entire movie plays.
startTime = time.time()
nextFrameTime = time.time()
lastFramePlayed = time.time()
timeout = timeoutInterval + time.time()
#print "Start Time: ", startTime
print startTime
while (frameDisplayed < movieLength):
	while (True): # while timer < 10ms
		if frameDisplayed == 5000 and pauseComplete == False:
			#print "Pause Time: ", time.time()
			pause()
			pauseComplete = True
			#print "Resume Time: ", time.time()
		elif frameDisplayed == 9000 and rewindComplete == False:
			#print "Rewind Time: ", time.time()
			rewind(7000)
			rewindComplete = True
		elif frameDisplayed == 10000:
			#print "Forward Time: ", time.time()
			forward(28000)
		receivePacket()
		if ((time.time() - packetReqTime[frameDisplayed]) > 3) and (frameBuffer[0] == ' '):
			requestPacket(str(frameDisplayed), random.randrange(4))
			#print "PACKET DROPPED:", frameDisplayed
			#print time.time()
			packetDrop = True
		if (time.time() > nextFrameTime):
			if (frameBuffer[0] != ' '):
				break
			elif (waiting == False):
				waiting = True
				#print "Waiting for frame:", frameDisplayed
	#end of while < 10ms
	
	# Our frames are indexed at 0, so technically frame 1 IS frame 0.
	#print "{Playing Frame: ", frameDisplayed, " with data: ", frameBuffer[0], "}"
	#print "----------------Displaying F#", (str(frameDisplayed)).zfill(5), "----------------"
	#print "Elapsed time: %.3f" %(time.time() - startTime)
	#print "Time between frames: %.3f" %(time.time() - lastFramePlayed)
	print time.time()
	waiting = False
	frameDisplayed += 1
	lastFramePlayed = time.time()
	nextFrameTime = time.time() + .01	# increment to 10ms in future
	# After display of frame, shift everything left
	frameBuffer[:31] = frameBuffer[1:]
	frameBuffer[31] = ' '
	#lastBufferFrame = False
	
	# ##################
	# CONGESTION LOGIC #
	# ##################
	congestionFactor = mean(serverPerformanceInst) - std(serverPerformanceInst) #CAN MAKE THIS CONSTANT AFTER TWEAKING
	if time.time() < timeout:
		for server in range(4):
			if (serverPerformanceInst[server] * 1) < congestionFactor:
				serverGoodList[server] = 0
			else:
				serverGoodList[server] = 1
		#print "Server Performance (Inst):", serverPerformanceInst
#		print "Standard Dev:", std(serverPerformanceInst)
#		print "Mean:", mean(serverPerformanceInst)
#		print "Factor:", congestionFactor
	else: # timeout occured
		timeout = time.time() + timeoutInterval
		#print "TIMEOUT"
		for servers in range(4):
			#packetsDroppedByServer[servers] = 0
			#packetsInFlight[server] = round(.5 * packetsInFlight[server]) # ????????????
			serverInstAvgRTT[servers] = 0.75 * mean(serverInstAvgRTT) # ??????????? maybe half distance between max & min?
			serverGoodList[servers] = 1
			serverRecvCountInst[servers] = 0
	
	# ###############
	# REQUEST LOGIC #
	# ###############
	serverReqThisCycle = [(1 + (1 * serverGoodList[i])) for i in range(4)] # All good get 2 reqs in beginning, bad get 1 req
	#print "serverInstAvgRTT:", serverInstAvgRTT
	#print "serverReqThisCycle:", serverReqThisCycle
	#print "Step 2"
	# Step 2: make list of unreq'd packets
	packetsToReq = [0 for i in range(len(packetsToReq))]
	count = 0
	for frame in range(32):
		if frameBuffer[frame] != ' ':
			continue
		if frameDisplayed + frame >= movieLength:
			break
		# Unreq'd packets in frameBuffer range
		case1 = (packetReqTime[frameDisplayed + frame] == 0)
		if not case1:
			# Requested a long time ago, in frameBuffer range
			case2 = ((time.time() - packetReqTime[frameDisplayed + frame]) > max(1.4 * serverAvgRTT[packetReqServer[frameDisplayed + frame]], 1.4 * serverInstAvgRTT[packetReqServer[frameDisplayed + frame]]))
		if (case1 or case2):
			#print "Case1:", case1, "Case2:", case2
			packetsToReq[count] = frameDisplayed + frame
			count += 1
			if count == (len(packetsToReq) - 1):
				break
	
	# If out of frameBuffer range but less than RTT
	if count < len(packetsToReq):
		for frame in range(32, int(min(serverAvgRTT) * 100)):
			if (frameDisplayed + frame >= movieLength) or (count == len(packetsToReq) - 1):
				break
			if (frameDisplayed + frame > OOBFrame + 32) and (time.time() > (OOBTime + 0.01 * (OOBFrame - frameDisplayed - 32)) and OOBFrame != 0):
				OOBFrame = 0
				break
			case3 = (packetReqTime[frameDisplayed + frame] == 0)
			if not case3:
				case4 = ((time.time() - packetReqTime[frameDisplayed + frame]) > max(1.3 * serverAvgRTT[packetReqServer[frameDisplayed + frame]], 1.3 * serverInstAvgRTT[packetReqServer[frameDisplayed + frame]]))
			if (case3 or case4):
				#print "Case3:", case3, "Case4:", case4
				packetsToReq[count] = frameDisplayed + frame
				count += 1
				if count == (len(packetsToReq) - 1):
					break
	
	# If out of frameBuffer range but will be in frameBuffer range in RTT
	if count < len(packetsToReq):
		for frame in range(int(min(serverAvgRTT) * 100), int(min(min(serverAvgRTT), min(serverInstAvgRTT)) * 100) + 14):
			if (frameDisplayed + frame >= movieLength) or (count == len(packetsToReq) - 1):
				break
			if (frameDisplayed + frame > OOBFrame + 32) and (time.time() > (OOBTime + 0.01 * (OOBFrame - frameDisplayed- 32)) and OOBFrame != 0):
				OOBFrame = 0
				break
			case5 = (packetReqTime[frameDisplayed + frame] == 0)
			if (case5):
				#print "Case5:", case5
				packetsToReq[count] = frameDisplayed + frame
				count += 1
	
	#print packetsToReq
	random.seed(int(time.time()))
	random.shuffle(roulette)
	'''for frame in range(2 + (sum(serverGoodList))): CHANGING XXXXXXXXXXXXXXXXXX'''
	for frame in range(len(packetsToReq)):
		if packetsToReq[frame] == 0:
			break
		if (serverGoodList[roulette[0]] == 1) and (serverReqThisCycle[roulette[0]] >= 2):
			requestPacket(str(packetsToReq[frame]), roulette[0])
			serverReqThisCycle[roulette[0]] -= 1
		elif (serverGoodList[roulette[1]] == 1) and (serverReqThisCycle[roulette[1]] >= 2):
			requestPacket(str(packetsToReq[frame]), roulette[1])
			serverReqThisCycle[roulette[1]] -= 1
		elif (serverGoodList[roulette[2]] == 1) and (serverReqThisCycle[roulette[2]] >= 2):
			requestPacket(str(packetsToReq[frame]), roulette[2])
			serverReqThisCycle[roulette[2]] -= 1
		elif (serverGoodList[roulette[3]] == 1) and (serverReqThisCycle[roulette[3]] >= 2):
			requestPacket(str(packetsToReq[frame]), roulette[3])
			serverReqThisCycle[roulette[3]] -= 1
		
		elif serverReqThisCycle[roulette[0]] >= 1:
			requestPacket(str(packetsToReq[frame]), roulette[0])
			serverReqThisCycle[roulette[0]] -= 1
		elif serverReqThisCycle[roulette[1]] >= 1:
			requestPacket(str(packetsToReq[frame]), roulette[1])
			serverReqThisCycle[roulette[1]] -= 1
		elif serverReqThisCycle[roulette[2]] >= 1:
			requestPacket(str(packetsToReq[frame]), roulette[2])
			serverReqThisCycle[roulette[2]] -= 1
		elif serverReqThisCycle[roulette[3]] >= 1:
			requestPacket(str(packetsToReq[frame]), roulette[3])
			serverReqThisCycle[roulette[3]] -= 1

	'''
	for frame in range(7, sum(serverGoodList), -1):
		if packetsToReq[frame] == 0:
			continue
		for i in range(4):
			if serverReqThisCycle[i] >= 1:
				requestPacket(str(packetsToReq[frame]), i)
				serverReqThisCycle[i] -= 1
	'''
	'''
	print "Step 3"
	# Step 3: If servers still have request(s) left, request either frame that appears next, or frame we've requested the longest time ago
	frame = 8
	while sum(serverReqThisCycle) > 0 and ((frame + frameDisplayed) <= movieLength):
		if (frame <= 31) and (frameBuffer[frame] == ' '):
			for i in range(4):
				if serverReqThisCycle[i] >= 1:
					requestPacket(str(frame + frameDisplayed), i)
					serverReqThisCycle[i] -= 1
					break
		frame += 1
	'''
for i in range(4):
	serverPerformance[i] = 1 / (serverAvgRTT[i] + (packetsDroppedByServer[i] * congestionFactor))
print "serverReqCount:", serverReqCount
print "serverRecvCount:", serverRecvCount
#print "serverInFightCount:", serverReqCount - serverRecvCount
print "Packets Dropped:", packetsDroppedByServer
print "Packets in Flight:", packetsInFlight
print "serverAvgRTT:", serverAvgRTT
print "Server Performance:", serverPerformance
print "Average time per frame" , (time.time() - startTime) / movieLength
print "Movie Time: ", time.time() - startTime

# Make sure to close everything once the video is finished.
s.close()
sys.stdout.close()