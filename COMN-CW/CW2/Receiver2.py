#/* Arbnor Bregu s1832263 */

from socket import *
import sys
import os


BUFF_SIZE = 1027

def main(argv):
    #parse command line arguements
    PORT = int(os.path.basename(argv[1]))
    FILENAME = os.path.basename(argv[2])

    #create the socket and bind the port number to PORT
    receiver_socket = socket(AF_INET, SOCK_DGRAM)
    receiver_socket.bind(('', PORT))

    #open a new file that can be written to
    file = open(FILENAME, 'wb+')

    #receive a packet from the socket, store the payload and sender address
    received_packet, sender_address = receiver_socket.recvfrom(BUFF_SIZE)

    #empty array to hold the sequence numbers of previously received packets
    last_sequence = None

    packets_received = 0
    total_acks_sent = 0


    print("<READY TO RECEIVE PACKETS>")
    while (received_packet):

        packets_received += 1

        #received_packet = bytearray(BUFF_SIZE)
        sequence_number_bytes = received_packet[0:2]
        end_of_file = received_packet[2:3]
        payload_data = received_packet[3:]
        

        ack = sequence_number_bytes #save the sequence number as ack


        if ack != last_sequence: #if the packet is new
            receiver_socket.sendto(ack, sender_address) #send the ack back to sender

            total_acks_sent += 1
            #end_of_file = int.from_bytes(end_of_file, 'big')

            if end_of_file == (1).to_bytes(1, 'big'): #if it is the final packet for the file
                file.write(payload_data)
                file.close()
                print("FILE HAS BEEN TRANSFERRED CORRECTLY")
                
                break
            #if its not the final packet do this
            print("sequence number %d has been saved correctly"% packets_received)

            file.write(payload_data)

            last_sequence = ack #update the list of already received packets


        else: #if the packet is a duplicate
            receiver_socket.sendto(ack, sender_address)
            total_acks_sent += 1
            continue #wait for the correct packet to be received.

        received_packet = receiver_socket.recvfrom(BUFF_SIZE)[0] #receive the next packet


    print("<PROCESS COMPLETE>")
    print("<TOTAL PACKETS RECEIVED %d>"%packets_received)
    print("<TOTAL ACKS SENT %d>"%total_acks_sent)

    file.close
    receiver_socket.close()
    
    

if __name__ == '__main__':
    main(sys.argv)

