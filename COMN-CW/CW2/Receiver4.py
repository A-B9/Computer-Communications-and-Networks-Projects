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


#this implementation could be for Receiver4, will know soon.
#def receiveAck():
def main(argv):

    PORT = int(os.path.basename(sys.argv[1]))
    FILENAME = os.path.basename(sys.argv[2])
    WINDOW = int(os.path.basename(sys.argv[3]))

    receiver_socket = socket(AF_INET, SOCK_DGRAM)
    receiver_socket.bind(('', PORT))

    #open a new file that can be written to
    file = open(FILENAME, 'wb+')

    base = 1
    next_seq = 1 + WINDOW

    window_tracker = []

    buffer_packets = []

    counter = 0

    print(f'ready to receive')

    while True:

        recv_packet, sender_addr = receiver_socket.recvfrom(BUFF_SIZE)

        seq_num, eof, payload = unpack_packet(recv_packet)

        print(f'packet: {seq_num}, has been received')

        #if it is the final packet
        if eof == 1:
            print(f' end of file')
            file.write(payload)

            print(f'seq_num {seq_num}, is equal to base {base}')
            file.write(payload)

            if not buffer_packets:
                print(f'write the payload of the buffered packets')
                for buff_pkt in buffer_packets:
                    file.write(buff_pkt)

            #move the base  up to the next unacked sequence number
            base = base + 1 + counter
            next_seq = next_seq + 1 + counter
            #update the window 
            window_tracker = [num for num in range(base, next_seq)]
            #reset the counter
            counter = 0
            #reset the buffer_packets
            buffer_packets = []

            ack_bytes = seq_num.to_bytes(2, 'big')
            receiver_socket.sendto(ack_bytes, sender_addr)
            receiver_socket.sendto(ack_bytes, sender_addr)


            break
            #break out of the situation

        #if the sequence number received is for a already received packet
        if seq_num < base:
            print(f'seqnum {seq_num}, is smaller than base {base}')
            ack_bytes = seq_num.to_bytes(2, 'big')
            receiver_socket.sendto(ack_bytes, sender_addr)


        #if ACK for first packet in window, write to file and update window
        if seq_num == base:
            
            print(f'seq_num {seq_num}, is equal to base {base}')
            file.write(payload)

            if buffer_packets:
            #if not buffer_packets:
                print(f'write the payload of the buffered packets')
                for buff_pkt in buffer_packets:
                    file.write(buff_pkt)

            #move the base  up to the next unacked sequence number
            base = base + 1 + counter
            next_seq = next_seq + 1 + counter
            #update the window 
            window_tracker = [num for num in range(base, next_seq)]
            #reset the counter
            counter = 0
            #reset the buffer_packets
            buffer_packets = []

            ack_bytes = seq_num.to_bytes(2, 'big')
            receiver_socket.sendto(ack_bytes, sender_addr)
        
        else:
            #if the packets are in the window but not in the first position
            if seq_num in window_tracker:
                #buffer the packet
                buffer_packets.append(payload)
                print(f'buffer packet {seq_num}')
                counter += 1

                ack_bytes = seq_num.to_bytes(2, 'big')
                receiver_socket.sendto(ack_bytes, sender_addr)


    file.close()
    receiver_socket.close()






if __name__ == '__main__':
    main(sys.argv)
