#/* Arbnor Bregu s1832263 */

from socket import *
import sys
import os

BUFF_SIZE = 1027 #same as payload size + header size 

def main(argv):

    PORT = int(os.path.basename(argv[1]))
    FILENAME = os.path.basename(argv[2])
    #PORT = port number which the receiver shall use to recevie messages
    #FILENAME = name to use for the recevied file, save the file with this name on local disk. 

    receiver_socket = socket(AF_INET, SOCK_DGRAM)
    receiver_socket.bind(('', PORT))

    file = open(FILENAME, 'wb+')

    received_packet = receiver_socket.recvfrom(BUFF_SIZE)

    while (received_packet):

        received_packet_bytes = bytearray(received_packet[0])

        sequence_number = received_packet_bytes[0:2]
        #sequence_number = int.from_bytes(sequence_number, 'big')
        end_of_file = received_packet_bytes[2]

        payload_data = received_packet_bytes[3:]

        if end_of_file == 1:
            file.write(payload_data)
            file.close
            print('<FILE HAS BEEN TRANSFERRED CORRECTLY>')
            break

        file.write(payload_data)

        received_packet = receiver_socket.recvfrom(BUFF_SIZE)

if __name__ == "__main__":
    main(sys.argv)