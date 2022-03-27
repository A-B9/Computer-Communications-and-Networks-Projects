# /* Arbnor Bregu s1832263 */

from socket import *
import sys
import os
import time
import math

BUFF_SIZE = 1024
HEADER_SIZE = 3

#need to create a logical timer that will begin when a packet is sent
#there must be one logical timer per packet.


#this function will create packets.
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

    HOST = os.path.basename(argv[1])
    PORT = int(os.path.basename(argv[2]))
    FILE = os.path.basename(argv[3])
    TIMEOUT = int(os.path.basename(argv[4])) / 1000
    WINDOW = int(os.path.basename(argv[5]))

    sender_socket = socket(AF_INET, SOCK_DGRAM)
    sender_socket.setblocking(0)
    print(f'socket has been created')

    file = open(FILE, 'rb')

    total_packets = math.ceil(os.path.getsize(FILE) / BUFF_SIZE)

    base = 1
    next_seq = 1 + WINDOW

    #lock = threading.Lock()

    #track the packets that have been received successfully
    window_packet_tracker = []
    #will turn to 1 before sending the final packet
    eof_flag = 0
    
    #once the final packet has been sent, turn to True
    file_sent = False

    #create the first window
    window_packet_tracker = [x for x in range(base, next_seq)]
    print(f'first window has been created.')

    #start the timer
    start_time = time.perf_counter()

    #Send the packets in the first window
    for seqnum in window_packet_tracker:
        read_file = file.read(BUFF_SIZE)
        send_file = make_packet(read_file, seqnum, eof_flag)
        sender_socket.sendto(send_file, (HOST, PORT))
        print(f'Send packet {seqnum}')

    #while the full file has not been delivered to the receiver.
    while (file_sent == False):
        try:
            #retreiev ack from the socket
            ack , sender_addr = sender_socket.recvfrom(2)
            ack = int.from_bytes(ack, 'big') #turn into an integer

            print(f'ACK receievd {ack}, base = {base}')

            #if its the ack for the first sequence number in the window
            if ack == base:
                
                #if the ack is for the final packet
                if ack == (total_packets):
                    file_sent = True
                    break
                
                #ack for base has been received, move window along
                base += 1
                
                if eof_flag != 1:
                    next_seq += 1

                #update the window.
                print(f'Update the window')
                window_packet_tracker = [x for x in range(base, next_seq)]

                if (next_seq - 1) == total_packets:
                    print(f'final packet reached.')
                    eof_flag = 1

                #send the next 
                read_file = file.read(BUFF_SIZE)
                send_file = make_packet(read_file, (next_seq -1), eof_flag)

                sender_socket.sendto(send_file, (HOST, PORT))
                print(f'new packet has been sent')
                print(f'sending packet {next_seq - 1}')
        except:
            continue

    total_time = time.perf_counter() - start_time
    throughput = round((os.path.getsize(FILE)/1000) / total_time)

    print(f'{throughput}')

    sender_socket.close()
    file.close()



if __name__ == '__main__':
    main(sys.argv)
