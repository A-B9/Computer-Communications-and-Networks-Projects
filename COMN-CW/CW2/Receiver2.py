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
    recv = receiver_socket.recvfrom(BUFF_SIZE)

    #empty array to hold the sequence numbers of previously received packets
    last_sequence = None

    packets_received = 0

    while (recv):
        
        received_packet = recv[0]
        sender_address = recv[1]
        
        seq_num = received_packet[0:2]
        eof = int.from_bytes(received_packet[2:3], byteorder='big')
        payload = received_packet[3:]

        if seq_num == last_sequence:
            incorrectAck = seq_num
            receiver_socket.sendto(incorrectAck, sender_address)
            continue

        else:
            if eof == 1:
                packets_received += 1
                last_sequence = seq_num
                file.write(payload)
                ack = seq_num
                receiver_socket.sendto(ack, sender_address)
                print("END O FILE")
                break
            
            packets_received += 1
            last_sequence = seq_num
            file.write(payload)
            ack = seq_num
            receiver_socket.sendto(ack, sender_address)

            recv = receiver_socket.recvfrom(BUFF_SIZE)

    print(packets_received)
    file.close()
    receiver_socket.close()

        

if __name__ == '__main__':
    main(sys.argv)

