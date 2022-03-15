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
    packet_no = 0

    while (received_packet):
        received_packet = bytearray(received_packet[0])
        sequence_number = int.from_bytes(received_packet[0:2], 'big')
        if sequence_number != packet_no:
            receiver_socket.sendto(sequence_number, sender_address)
            continue

        end_of_file = received_packet[2]
        payload_data = received_packet[3:]

        if end_of_file == 1:
            file.write(payload_data)
            file.close()
            print('<FILE HAS BEEN TRANSFERRED CORRECTLY>')
            break

        file.write(payload_data)

        received_packet = receiver_socket.recvfrom(BUFF_SIZE)
    
    receiver_socket.close()

if __name__ == '__main__':
    main(sys.argv)

