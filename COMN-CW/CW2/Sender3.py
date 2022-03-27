# /* Arbnor Bregu */

from socket import *
import sys
import os
import time
import math

BUFF_SIZE = 1024
HEADER_SIZE = 3


def make_packet(data, sequence_number, eof):
    sequence_number = sequence_number.to_bytes(2, 'big')
    eof = eof.to_bytes(1, 'big')
    payload = bytearray(data)

    send_file = bytearray(HEADER_SIZE + BUFF_SIZE)
    send_file[0:2] = sequence_number
    send_file[2:3] = eof
    send_file[3:] = payload

    return send_file


def main(argv):
    
    #command line arguements
    HOST = os.path.basename(argv[1])
    PORT = int(os.path.basename(argv[2]))
    FILE = os.path.basename(argv[3])
    TIMEOUT = int(os.path.basename(argv[4])) / 1000 #in miliseconds
    WINDOW = int(os.path.basename(argv[5]))

    sender_socket = socket(AF_INET, SOCK_DGRAM) #create socket
    sender_socket.setblocking(0)

    file = open(FILE, 'rb') #open the file to be read
    
    total_packets = math.ceil(os.path.getsize(FILE) / BUFF_SIZE)

    base = 1
    next_seq = 1

    true_start = time.time()

    while next_seq != total_packets:
        try:
            resend_packets = []
            while (next_seq < base + WINDOW) and (next_seq != total_packets):
                read_file = file.read(BUFF_SIZE)
                send_file = make_packet(read_file, next_seq, 0)

                resend_packets.append(send_file)

                sender_socket.sendto(send_file, (HOST, PORT))

                if base == next_seq:
                    sender_socket.settimeout(TIMEOUT)
                next_seq += 1

            print(f'window has been sent, next_seq is {next_seq}')

            receiveAck = False
            correctAck = False
            while (correctAck == False):
                try:
                    base, sender_addr = sender_socket.recvfrom(2)
                    base = int.from_bytes(base, 'big') + 1
                    receiveAck = True

                    if (base == next_seq) and (receiveAck == True):
                        sender_socket.settimeout(0)
                        correctAck = True
                        break
                    else:
                        sender_socket.settimeout(TIMEOUT)
                        continue
                except timeout:

                    for packet in resend_packets:
                        sender_socket.sendto(packet, (HOST, PORT))
                    
                    continue
        except:
            continue


    try:
        if (next_seq == total_packets):
            read_file = file.read(BUFF_SIZE)
            send_file = make_packet(read_file, next_seq, 1)
            sender_socket.sendto(send_file, (HOST, PORT))

            if base == next_seq:
                sender_socket.settimeout(TIMEOUT)
            next_seq += 1

            receiveAck = False
            correctAck = False
            while correctAck == False:
                try:
                    base, sender_addr = sender_socket.recvfrom(2)
                    base = int.from_bytes(base, 'big') + 1
                    receiveAck = True
                    if (base == next_seq) and (receiveAck == True):
                        sender_socket.settimeout(0)
                        correctAck = True
                    else:
                        sender_socket.settimeout(TIMEOUT)
                except timeout:
                    sender_socket.sendto(send_file, (HOST, PORT))
                    continue
        print(f'final packet has been sent')
    except:
        print('')

    file.close()
    sender_socket.close()

    total_time = time.time() - true_start
    throughput = round((os.path.getsize(FILE) / 1000) / total_time)

    print(f'Throughput: {throughput}')

        
            
        





if __name__ == '__main__':
    main(sys.argv)

