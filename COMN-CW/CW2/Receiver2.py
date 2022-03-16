#/* Arbnor Bregu s1832263 */

from socket import *
import sys
import os
import time


BUFF_SIZE = 1027

def main(argv):

    PORT = int(os.path.basename(argv[1]))
    FILENAME = os.path.basename(argv[2])

    receiver_socket = socket(AF_INET, SOCK_DGRAM)
    receiver_socket.bind(('', PORT))

    file = open(FILENAME, 'wb+')

    received_packet, sender_address = receiver_socket.recvfrom(BUFF_SIZE)

    last_sequence = None

    print("<READY TO RECEIVE PACKETS>")

    while (received_packet):

        received_packet = bytearray(received_packet)

        sequence_number_bytes = received_packet[0:2]
        #sequence_number = int.from_bytes(sequence_number_bytes, 'big')

        print("sequence number has been saved correctly")

        end_of_file = received_packet[2:2]
        payload_data = received_packet[3:]

        if sequence_number_bytes == last_sequence:
            print("WRONG SEQUENCE NUMBER: SEND NAK TO SENDER")
            receiver_socket.sendto(sequence_number_bytes, sender_address)
            continue
        else:
            if end_of_file == 1:
                file.write(payload_data)
                file.close()
                print('<FILE HAS BEEN TRANSFERRED CORRECTLY>')
                break

            file.write(payload_data)
            
            last_sequence = sequence_number_bytes
        

        received_packet = receiver_socket.recvfrom(BUFF_SIZE)

        print("PACKET NUMBER %d HAS BEEN RECEIVED")
    
    
    receiver_socket.close()

if __name__ == '__main__':
    main(sys.argv)

