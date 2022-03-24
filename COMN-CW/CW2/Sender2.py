#/* Arbnor Bregu s1832263 */

from socket import *
import sys
import os
import time
import math

BUFF_SIZE = 1024 #Buffer size
HEADER_SIZE = 3 #Size of header

def main(argv):

    #command line arguements
    HOST = os.path.basename(argv[1])
    PORT = int(os.path.basename(argv[2]))
    FILE = os.path.basename(argv[3])
    TIMEOUT = int(os.path.basename(argv[4])) / 1000 #in miliseconds

    sender_socket = socket(AF_INET, SOCK_DGRAM) #create socket
    file = open(FILE, 'rb') #open the file to be read
    read_file = file.read(BUFF_SIZE) #read the file in chunks of size 1024

    packet_no = 1 #keep track of the packet being sent

    re_transmit = 0 #Track retransmissions
    file_size = 0 #Track the size of the file, needed to calculate throughput

    start_time = time.time()

    while (read_file): #while read_file has data
        if (len(read_file) < BUFF_SIZE):#if the length of read_file is less than BUFF_SIZE, that indicates its the last packet
            break #break out of the while loop
        
        #store the sequence number, EOF flag and payload as bytes and create a packet, that is called send_file
        seq_num = packet_no.to_bytes(2, byteorder='big')
        eof = (0).to_bytes(1, byteorder='big')
        payload = bytearray(read_file)

        send_file = bytearray(HEADER_SIZE + BUFF_SIZE)
        send_file[0:2] = seq_num
        send_file[2:3] = eof
        send_file[3:] = payload

        sender_socket.sendto(send_file, (HOST, PORT)) #send the packet to the receiver

        correctAck = False
        receiveAck = False

        while (correctAck == False): #while correctAck is False
            try:
                sender_socket.settimeout(TIMEOUT)#set the socket to timeout after TIMEOUT seconds
                ack, sender_addr = sender_socket.recvfrom(2)#receive in a 2 byte packet from the socket
                ack = ack[0:2] #make sure to only store the first 2 bytes of the ACK packet
                receiveAck = True #set to True because an ACK has been received

            except socket.timeout:
                receiveAck = False #if the socket times out, keep receiveAck as false
                sender_socket.sendto(send_file, (HOST, PORT))
                re_transmit += 1

            if receiveAck == True:
                if ack == seq_num:
                    correctAck = True
                    break
        
        file_size += len(read_file)
        packet_no += 1
        read_file = file.read(BUFF_SIZE)

    if len(read_file) < BUFF_SIZE:
        seq_num = packet_no.to_bytes(2, byteorder='big')
        eof = (1).to_bytes(1, byteorder='big')

        payload = bytearray(read_file)

        send_file = bytearray(HEADER_SIZE + BUFF_SIZE)
        send_file[0:2] = seq_num
        send_file[2:3] = eof
        send_file[3:] = payload

        sender_socket.sendto(send_file, (HOST, PORT))

        while (correctAck == False):
            try:
                sender_socket.settimeout(TIMEOUT)
                ack, sender_addr = sender_socket.recvfrom(2)
                ack = ack[0:2]
                receiveAck = True
            except socket.timeout:
                receiveAck = False
                sender_socket.sendto(send_file, (HOST, PORT))
                re_transmit += 1

            if receiveAck == True:
                if ack == seq_num:
                    correctAck = True
                    break
    
        file_size += len(read_file)
        packet_no += 1


    total_time_taken = time.time() - start_time #calculate total runtime of the program once all packets sent
    file_size_kb = file_size / 1000 #get the file size in KB instead of just bytes
    throughput = round(file_size_kb / total_time_taken) #calculate throughput

    print("Number of retransmissions: " +str(re_transmit) + ", Throughput: " + str(throughput)) #necessary output

    file.close() #close file
    sender_socket.close() #close socket







if __name__ == "__main__":
    main(sys.argv)
    
