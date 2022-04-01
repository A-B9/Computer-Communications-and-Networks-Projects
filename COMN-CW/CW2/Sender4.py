# /* Arbnor Bregu s1832263 */

from socket import *
import sys
import os
import time
import math
import threading

BUFF_SIZE = 1024
HEADER_SIZE = 3

HOST = os.path.basename(sys.argv[1])
PORT = int(os.path.basename(sys.argv[2]))
FILE = os.path.basename(sys.argv[3])
TIMEOUT = int(os.path.basename(sys.argv[4])) / 1000
WINDOW = int(os.path.basename(sys.argv[5]))

sender_socket = socket(AF_INET, SOCK_DGRAM)
print(f'socket has been created')

file = open(FILE, 'rb')
total_packets = math.ceil(os.path.getsize(FILE) / BUFF_SIZE)
lock = threading.Lock()

base = 1
next_seq = 1
eof = 0

#tracks the window
current_window = [None] * WINDOW
#will track which sequence number in the window has been acked.
is_window_acked = [False] * WINDOW

start_time = time.perf_counter()

file_sent = False

#will create the packet
def make_packet(data, sequence_number, eof):
    sequence_number = sequence_number.to_bytes(2, 'big')
    eof = eof.to_bytes(1, 'big')
    payload = bytearray(data)

    send_file = bytearray(HEADER_SIZE + BUFF_SIZE)
    send_file[0:2] = sequence_number
    send_file[2:3] = eof
    send_file[3:] = payload

    return send_file

def packet_timeout(current_packet_seq):
    lock.acquire()
    if (current_packet_seq < base) or (is_window_acked[current_packet_seq - base]):
        lock.release()
        return

    print(f'Packet: {current_packet_seq}, has timed out, will retransmit.')
    #resend packet if timeout occurs.
    sender_socket.sendto(current_window[current_packet_seq - base], (HOST, PORT))
    print(f'resending packet {current_packet_seq - base}')
    timer = threading.Timer(TIMEOUT, packet_timeout, args=(current_packet_seq, ))
    timer.start()
    print(f'Timer has been started')
    lock.release()

def send_thread_function():
    global current_window
    global start_time
    global total_packets
    global eof
    global next_seq

    while True: #infinite loop
        lock.acquire()
        while (next_seq < base + WINDOW):

            payload = file.read(BUFF_SIZE)
            eof_flag = eof
            if next_seq == total_packets:
                eof = 1
                eof_flag = eof
            print(f'made next packet: {next_seq}')
            send_file = make_packet(payload, next_seq, eof_flag)

            if next_seq == 1:
                start_time = time.perf_counter()

            print(f'next packet in the window has been delivered')

            #current_pos = next_seq - base
            current_window[next_seq - base] = send_file

            print(f'Sending packet {next_seq}')

            sender_socket.sendto(send_file, (HOST, PORT))

            timer = threading.Timer(TIMEOUT, packet_timeout, args=(next_seq,))
            timer.start()

            next_seq += 1

            if eof == 1:
                lock.release()
                return

        lock.release()
        time.sleep(0.01)

def receive_thread_function():
    global current_window
    global is_window_acked
    global base

    while True:
        ack, sender_addr = sender_socket.recvfrom(2)

        lock.acquire()

        ack = int.from_bytes(ack, 'big')
        print(f'received ACK {ack}')
        #update_current_window(ack)

        if (ack >= base):
            #current_position = ack - base
            is_window_acked[ack - base] = True
            print(f'acks have been updated')
            print(is_window_acked)

            while (is_window_acked[0] == True):
                print(f'Base in window has been acked, delete and update window by one.')

                del current_window[0]
                current_window.append(None)

                del is_window_acked[0]
                is_window_acked.append(False)

                print(is_window_acked)

                base = base + 1



        print(f'ACK = {ack}, current base = {base}')

        if (base > total_packets):
            print(f'Base is larger than the final seq_num: {base}')

            total_time = time.perf_counter() - start_time
            throughput = round((os.path.getsize(FILE) / 1000) / total_time)

            print(f'{throughput}')
            print(f'PROCESS COMPLETE')

            lock.release()
            return
        
        lock.release()

print(f'generate the threads')
send_thread = threading.Thread(target=send_thread_function)
receive_thread = threading.Thread(target=receive_thread_function)

print(f'start the threads')
send_thread.start()
receive_thread.start()

print(f'join the threads')
send_thread.join()
receive_thread.join()

file.close()
sender_socket.close()