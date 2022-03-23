#/* Arbnor Bregu s1832263 */

from socket import *
import sys
import os
import time

BUFF_SIZE = 1024 #Buffer size
HEADER_SIZE = 3 #Size of header

def main(argv):

    #command line arguements
    HOST = os.path.basename(argv[1])
    PORT = int(os.path.basename(argv[2]))
    FILE = os.path.basename(argv[3])
    TIMEOUT = int(os.path.basename(argv[4])) #in miliseconds


    sender_socket = socket(AF_INET, SOCK_DGRAM) #create socket
    file = open(FILE, 'rb') #open the file to be read
    read_file = file.read(BUFF_SIZE) #read the file in chunks of size 1024

    packet_no = 0 #keep track of the packet being sent
    eof = (0).to_bytes(1, byteorder='big')

    re_transmit = 0 #Track retransmissions
    file_size = 0 #Track the size of the file, needed to calculate throughput

    start_time = time.time()
    print(len(read_file))

    total_packets =  round(len( bytearray( file.read()) ) / 1024)
    print(total_packets)

    receiveAck = False
    correctAck = False


    while(read_file):
        
        print('hello world')

        print("SEND PACKET %d"%packet_no)
        seq_num = packet_no.to_bytes(2, byteorder='big')
        payload = bytearray(read_file)

        send_file = bytearray(HEADER_SIZE + BUFF_SIZE)
        send_file[0:2] = seq_num
        send_file[2:3] = eof
        send_file[3:] = payload

        sender_socket.sendto(send_file, (HOST, PORT))


        while (correctAck == False):
            try:
                sender_socket.settimeout(TIMEOUT * 0.001)
                ack, sender_addr = sender_socket.recvfrom(2)
                ack = ack[0:2]
                receiveAck = True

            except socket.timeout:
                receiveAck = False

            if receiveAck == True:
                if ack == seq_num:
                    correctAck = True
                    print("CORRECT ACK")
                    break
            else:
                sender_socket.sendto(send_file, (HOST, PORT))
                re_transmit += 1
        
        print("update read_file")
        file_size += len(read_file)
        print('file size %d'%file_size)
        
        packet_no += 1

        read_file = file.read(BUFF_SIZE)

        print(len(read_file))

    print('length of file is smaller than buff_size')
    print(len(read_file))

    if (len(read_file) < BUFF_SIZE):
        print('FINAL PACKET')
        print("SEND PACKET %d"%packet_no)
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
                sender_socket.settimeout(TIMEOUT * 0.001)
                ack, sender_addr = sender_socket.recvfrom(2)
                ack = ack[0:2]
                receiveAck = True
            except socket.timeout:
                receiveAck = False
            if receiveAck == True:
                if ack == seq_num:
                    correctAck = True
                    print("CORRECT ACK")
            else:
                sender_socket.sendto(send_file, (HOST, PORT))
                re_transmit += 1
    
        file_size += len(read_file)

        packet_no += 1


    print('i am here for whatever reason')
    total_time_taken = time.time() - start_time #calculate total runtime of the program once all packets sent
    throughput = round(file_size / total_time_taken) #calculate throughput

    print("Number of retransmissions: " +str(re_transmit) + ", Throughput: " + str(throughput)) #necessary output

    file.close() #close file
    sender_socket.close() #close socket







if __name__ == "__main__":
    main(sys.argv)
    
