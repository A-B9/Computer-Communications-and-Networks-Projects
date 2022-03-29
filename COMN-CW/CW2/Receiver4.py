

from socket import *
import os
import sys

BUFF_SIZE = 1027


PORT = int(os.path.basename(sys.argv[1]))
FILENAME = os.path.basename(sys.argv[2])
WINDOW = int(os.path.basename(sys.argv[3]))
receiver_socket = socket(AF_INET, SOCK_DGRAM)
receiver_socket.bind(('', PORT))
#open a new file that can be written to
file = open(FILENAME, 'wb+')

window_tracker = [None] * WINDOW

base = 1
next_seq = 1

final_seq = 0

file_recv = False

#counter = 1

def unpack_packet(packet):
    seq_num = int.from_bytes(packet[0:2], 'big')
    eof = int.from_bytes(packet[2:3], 'big')
    payload = packet[3:]
    return seq_num, eof, payload

def recv_update_window(packet):
    global base
    global window_tracker
    global next_seq

    seq_num, eof, payload = unpack_packet(packet)
    if (base > seq_num):
        return
    
    current_pos = seq_num - base
    window_tracker[current_pos] = packet

    while (window_tracker[0] != None):
        seq_num_win, eof_win, payload = unpack_packet(window_tracker[0])

        file.write(payload)

        del window_tracker[0]

        window_tracker.append(None)
        base += 1


#receiver Loop

while file_recv == False:

    
    data, sender_addr = receiver_socket.recvfrom(BUFF_SIZE)

    seq_num, eof, payload = unpack_packet(data)

    print(f'received PKT {seq_num}')

    if seq_num >= base - WINDOW:
        seq_num_bytes = (seq_num).to_bytes(2, 'big')
        receiver_socket.sendto(seq_num_bytes, sender_addr)

    recv_update_window(data)

    if eof == 1:
        print(f'final packet recevied')
        final_seq = seq_num

        file_recv = True



print(f'file has been received')

file.close()
receiver_socket.close()