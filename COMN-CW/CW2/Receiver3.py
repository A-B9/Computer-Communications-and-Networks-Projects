# /* Arbnor Bregu */

from socket import *
import os
import sys

BUFF_SIZE = 1027

def unpack_packet(packet):
    seq_num = int.from_bytes(packet[0:2], 'big')
    eof = int.from_bytes(packet[2:3], 'big')
    payload = packet[3:]
    return seq_num, eof, payload

def main(argv):

    #parse command line arguements
    PORT = int(os.path.basename(argv[1]))
    FILENAME = os.path.basename(argv[2])

    #create the socket and bind the port number to PORT
    receiver_socket = socket(AF_INET, SOCK_DGRAM)
    receiver_socket.bind(('', PORT))

    #open a new file that can be written to
    file = open(FILENAME, 'wb+')

    expected_seqnum = 1

    while True:
        recv = receiver_socket.recvfrom(BUFF_SIZE)

        recv_packet = recv[0]
        sender_addr = recv[1]

        seq_num, eof, payload = unpack_packet(recv_packet)

        if seq_num != expected_seqnum:
            expected_seqnum_bytes = (expected_seqnum - 1).to_bytes(2, 'big')
            receiver_socket.sendto(expected_seqnum_bytes, sender_addr)
            continue
        else:
            if eof == 1:
                file.write(payload)
                expected_seqnum_bytes = expected_seqnum.to_bytes(2, 'big')
                receiver_socket.sendto(expected_seqnum_bytes, sender_addr)
                receiver_socket.sendto(expected_seqnum_bytes, sender_addr)
                receiver_socket.sendto(expected_seqnum_bytes, sender_addr)

                print('END OF FILE')
                expected_seqnum += 1
                break

            file.write(payload)
            expected_seqnum_bytes = expected_seqnum.to_bytes(2, 'big')
            receiver_socket.sendto(expected_seqnum_bytes, sender_addr)
        expected_seqnum += 1

    
    file.close()
    receiver_socket.close()

if __name__ == '__main__':
    main(sys.argv)

