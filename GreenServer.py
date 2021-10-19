import sys
from socket import *

# Set print destination for later log file
sys.stdout = open('server_log', 'w')
# Set server name and port
serverPort = 13000
packetLength = 1029 # length(frameNumber) + length(frameData)
frameNumber = 0
# Create server sockets and bind
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
#print "The server is ready to receive"
#read moive from a file
#fo = open("movie.txt", "rb")
# Wait for packet to arrive
frameData = str(0).zfill(1024)
while 1:
	# Receive data packets
	frameNumber,clientAddress = serverSocket.recvfrom(5)
	# Debug variables, commented out for release
	#frameNumber, speedAdjust = packet.split(';')
	#frameNumber = fnpacket
	#frameData = str(randrange(1,8191)) # Generate random data for movie frame//make sure size =1024
	#fo.seek(int(frameNumber)*(packetLength - 6),0)
	#frameData=fo.read(packetLength - 6)
	#frameData = stri.zfill(1024)
	#print "frameData: " + frameData
	# speedAdjust
	# Create response and send
	mfpacket = frameNumber.zfill(5) + frameData
	serverSocket.sendto(mfpacket,clientAddress)
	# Print response to server_log
	#print frameNumber
fo.close()