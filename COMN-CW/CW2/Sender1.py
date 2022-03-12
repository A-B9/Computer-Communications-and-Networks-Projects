#/* Arbnor Bregu s1832263 */

from socket import *
import sys
import os

BUFF_SIZE = 1024 #equivalent to payload length

HOST_NAME, HOST_PORT, FILENAME = os.path.basename(sys.argv[1:-1])
#HOST = IP address or host name for the receiver
#PORT = port number of the receiver
#FILENAME = the file to transfer to the receiver

BANDWIDTH = 10 #bandwidth is 10Mbps
PROP_DELAY = 5 #propogation delay = 5ms (1 way delay), 0% packet loss

senderSocket = socket(AF_INET, SOCK_DGRAM)

#senderSocket.sendto(fileToSend.encode(), (HOST_NAME, HOST_PORT))
