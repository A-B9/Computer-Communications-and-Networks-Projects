#/* Arbnor Bregu s1832263 */

from socket import *
import sys
import os

BUFF_SIZE = 1024 #same as payload size

PORT, FILENAME = os.path.basename(sys.argv[1:-1])
#PORT = port number which the receiver shall use to recevie messages
#FILENAME = name to use for the recevied file, save the file with this name on local disk. 
