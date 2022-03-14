#/* Arbnor Bregu s1832263 */

from socket import *
import sys
import os


def main(argv):

    BUFF_SIZE = 1024 #equivalent to payload length
    HEADER_SIZE = 3

    HOST_NAME = os.path.basename(argv[1])
    HOST_PORT = int(os.path.basename(argv[2]))
    FILE = os.path.basename(argv[3])

    senderSocket = socket(AF_INET, SOCK_DGRAM)

    file = open(FILE, 'rb') #read the file (store it in file). 'r' means we read the file, 'b' means binary mode such as images.
    read_file = file.read(BUFF_SIZE)
    packet_no = 0

    while (read_file):
        #if eof = 0, not the end of the fileSe
        #if eof = 1, it is the end of the file
        end_of_file = (0).to_bytes(1, 'big')

        print(len(read_file)) #testing line

        if (len(read_file) < BUFF_SIZE):
            end_of_file = (1).to_bytes(1, 'big')
        
        sequence_number = packet_no.to_bytes(2, 'big')
        
        file_to_send = bytearray(BUFF_SIZE + HEADER_SIZE)
        file_to_send[0:1] = sequence_number #sequence number is 2 bytes long, starts from the index 0 and occupies both index 0 and 1
        file_to_send[2:3] = end_of_file #end of file flag is 1 byte long and is directly after the sequence number, therefore it occupies index 2
        file_to_send[3:] = bytearray(read_file) #the payload occupies the rest of the packet and starts after the end of file flag, therefore it occupies every index on and after index 3

        senderSocket.sendto(file_to_send, (HOST_NAME, HOST_PORT))

        read_file = file.read(BUFF_SIZE)
        packet_no += 1
    
    file.close()

if __name__ == "__main__":
    main(sys.argv)
