#/* Arbnor Bregu s1832263 */

from socket import *
import sys
import os
import time

BUFF_SIZE = 1024
HEADER_SIZE = 3

def main(argv):
    HOST_NAME = os.path.basename(argv[1])
    HOST_PORT = int(os.path.basename(argv[2]))
    FILE = os.path.basename(argv[3])
    RETRY_TIMEOUT = int(os.path.basename(argv[4]))/1000

    sender_socket = socket(AF_INET, SOCK_DGRAM)

    file = open(FILE, 'rb')

    read_file = file.read(BUFF_SIZE)

    packet_no = 0

    re_transmit = 0

    while (read_file):
        end_of_file = (0).to_bytes(1, 'big')

        if len(read_file) < BUFF_SIZE:
            end_of_file = (1).to_bytes(1, 'big')

        sequence_number = packet_no.to_bytes(2, 'big')

        file_to_send = bytearray(BUFF_SIZE + HEADER_SIZE)
        file_to_send[0:1] = sequence_number
        file_to_send[2:3] = end_of_file
        file_to_send[3:] = bytearray(read_file)

        sender_socket.sendto(file_to_send, (HOST_NAME, HOST_PORT))
        start_timer = time.time()

        if sender_socket.recvfrom(2):
            ack = sender_socket.recvfrom(2)
            if sequence_number == ack:
                stop_timer = time.time()
                break
            else:
                sender_socket.sendto(file_to_send, (HOST_NAME, HOST_PORT))
                re_transmit += 1
                continue
        if start_timer == float(RETRY_TIMEOUT):
            sender_socket.sendto(file_to_send, (HOST_NAME, HOST_PORT))
            re_transmit += 1
            continue

        read_file = file.read(BUFF_SIZE)
        packet_no += 1

    file.close()

if __name__ == "__main__":
    main(sys.argv)
    
