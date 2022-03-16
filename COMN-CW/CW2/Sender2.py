#/* Arbnor Bregu s1832263 */

from socket import *
import sys
import os
import time
import select

BUFF_SIZE = 1024 #Buffer size
HEADER_SIZE = 3 #Size of header

def main(argv):




    #command line arguements
    HOST_NAME = os.path.basename(argv[1])
    HOST_PORT = int(os.path.basename(argv[2]))
    FILE = os.path.basename(argv[3])
    RETRY_TIMEOUT = int(os.path.basename(argv[4])) #in miliseconds


    sender_socket = socket(AF_INET, SOCK_DGRAM) #create socket
    file = open(FILE, 'rb') #open the file to be read
    read_file = file.read(BUFF_SIZE) #read the file in chunks of size 1024
    packet_no = 0 #keep track of the packet being sent

    re_transmit = 0 #Track retransmissions
    total_transmissions = 0 #Track total transmissions
    file_size = 0 #Track the size of the file, needed to calculate throughput






    true_start = time.time() #Start the timer to calculate true runtime of the program

    while (read_file): #While there are still chunks of data left 
        end_of_file = (0).to_bytes(1, 'big') #EOF flag set to 0

        if len(read_file) < BUFF_SIZE: #When the size of the is smaller than buffer size
            end_of_file = (1).to_bytes(1, 'big') #Set eof flag to 0, indicates end of the file has been reached
            print("<END OF FILE>")

        sequence_number = packet_no.to_bytes(2, 'big') #store the sequence number of the packet

        file_to_send = bytearray(BUFF_SIZE + HEADER_SIZE) #Create bytearray to store the data of the packet
        file_to_send[0:2] = sequence_number #Store the sequence number, 2 bytes
        file_to_send[2:3] = end_of_file #Store the eof flag, 1 byte
        file_to_send[3:] = bytearray(read_file) #Store payload data
        print("<SENDING PACKET %d>"%packet_no)


        sender_socket.sendto(file_to_send, (HOST_NAME, HOST_PORT)) #Send to receiver
        total_transmissions += 1 #When packet has been transmitted, increment total counter

        socket_timer = milisecondTimer() #start countdown timer

        ###### up to here everything is standard and should work perfect #########
        while True:
            wait_for_ack = select.select([sender_socket], [], [], 0)
            wait_for_ack = wait_for_ack[0]

            if wait_for_ack: #If the receiver contains a 2 byte packet 

                ack = wait_for_ack[0].recvfrom(2) #store the 2 byte packet as the ACK
                ack = ack[0:2]
                if sequence_number == ack: #if the ack is equal to the current sequence number
                    #packet has been received  correctly 
                    print("<PACKET %d DELIVERED>"%packet_no)
                    break #break out of the loop to continue sending the next packet

                else: #if the ack is not correct
                    print("<INCORRECT ACK RECEIVED, WILL WAIT>") #does nothing
                    continue
            else: #if no packets received
                if next(socket_timer) > RETRY_TIMEOUT: #if the timer is equal to or exceeds RETRY_TIMEOUT
                
                #from the rdt3.0 FSM we must resend the packet and start the timer again.

                    sender_socket.sendto(file_to_send, (HOST_NAME, HOST_PORT))#Resend the packet
                    re_transmit += 1
                    total_transmissions += 1
                    socket_timer = milisecondTimer()

                    print("<RETRANSMISSION NUMBER: %d"%re_transmit)
                    continue

        
        file_size = file_size + len(read_file) #count the total bytes of the file sent so far
        read_file = file.read(BUFF_SIZE) #read in the next 1024 bytes of the file
        packet_no += 1 #increment the packet number to indicate the process is moving to the next packet

        #time.sleep(0.005)
        print("<TRANSMITTING NEXT PACKET, PACKET NO %d"%packet_no)


    total_time_taken = time.time() - true_start #calculate total runtime of the program once all packets sent
    throughput = (file_size / total_time_taken) #calculate throughput

    print("Number of retransmissions: " + re_transmit + ", Throughput: " + throughput) #necessary output

    file.close() #close file
    sender_socket.close() #close socket


def milisecondTimer():

    start_time = time.time() * 1000 #1000 seconds in a milisecond. so *1000 to get current time in miliseconds.
    while True: #loop forever
        yield time.time() * 1000 - start_time #get the time difference




if __name__ == "__main__":
    main(sys.argv)
    
