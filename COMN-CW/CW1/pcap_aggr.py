from scapy.utils import RawPcapReader
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP
from ipaddress import ip_address, ip_network
import sys
import matplotlib.pyplot as plt

class Node(object):
    def __init__(self, ip, plen):
        self.bytes = plen
        self.left = None
        self.right = None
        self.ip = ip
    def add(self, ip, plen):
        #
        # write your code here
        #
        if self.ip < ip:
            if self.right != None:
                self.right.add(ip,plen)
            else:
                self.right = Node(ip,plen)
        elif ip < self.ip:
            if self.left!= None:
                self.left.add(ip, plen)
            else:
                self.left = Node(ip, plen)
        else:
            self.bytes = self.bytes + plen

    def data(self, data):
        if self.left:
            self.left.data(data)
        if self.bytes > 0:
            data[ip_network(self.ip)] = self.bytes
        if self.right:
            self.right.data(data)
    @staticmethod

    def supernet(ip1, ip2):
        # arguments are either IPv4Address or IPv4Network
        na1 = ip_network(ip1).network_address
        na2 = ip_network(ip2).network_address
        #
        # write your code here
        #
        bna1, bna2= '{0:32b}'.format(int(na1)), '{0:32b}'.format(int(na2))

        netmask = 0
        common_prefix = ''
        for x in range(1, 33):
            if bna1[0:x] == bna2[0:x]:
                common_prefix = bna1[0:x]
                netmask = x
                if netmask == 32:
                    break
        if common_prefix == '':
            binary_to_ip = 0
        else:
            full_binary = common_prefix + ('0' * (32 - netmask))
            binary_to_ip = int(full_binary, 2)
        na1 = ip_address(binary_to_ip)
        return ip_network('{}/{}'.format(na1, netmask), strict=False)

    def aggr(self, byte_thresh):
        if self.right != None:
            if self.right.right != None or self.right.left != None:
                self.right.aggr(byte_thresh)
            if self.right.bytes < byte_thresh:
                self.ip = self.supernet(self.ip, self.right.ip)
                self.bytes += self.right.bytes
                self.right.bytes = 0
                if self.right.right == None:
                    if self.right.left == None:
                        self.right = None

        if self.left != None:
            if self.left.left != None or self.left.right != None:
                self.left.aggr(byte_thresh)
            if self.left.bytes < byte_thresh:
                self.ip = self.supernet(self.ip, self.left.ip)
                self.bytes = self.bytes + self.left.bytes
                self.left.bytes = 0
                if self.left.left == None:
                    if self.left.right == None:
                        self.left = None

class Data(object):
    def __init__(self, data):
        self.tot_bytes = 0
        self.data = {}
        self.aggr_ratio = 0.05
        root = None
        cnt = 0
        for pkt, metadata in RawPcapReader(data):
            ether = Ether(pkt)
            if not 'type' in ether.fields:
                continue
            if ether.type != 0x0800:
                continue
            ip = ether[IP]
            self.tot_bytes += ip.len
            if root is None:
                root = Node(ip_address(ip.src), ip.len)
            else:
                root.add(ip_address(ip.src), ip.len)
            cnt += 1
        root.aggr(self.tot_bytes * self.aggr_ratio)
        root.data(self.data)
    def Plot(self):
        data = {k: v/1000 for k, v in self.data.items()}
        plt.rcParams['font.size'] = 8
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.grid(which='major', axis='y')
        ax.tick_params(axis='both', which='major')
        ax.set_xticks(range(len(data)))
        ax.set_xticklabels([str(l) for l in data.keys()], rotation=45,
            rotation_mode='default', horizontalalignment='right')
        ax.set_ylabel('Total bytes [KB]')
        ax.bar(ax.get_xticks(), data.values(), zorder=2)
        ax.set_title('IPv4 sources sending {} % ({}KB) or more traffic.'.format(
            self.aggr_ratio * 100, self.tot_bytes * self.aggr_ratio / 1000))
        plt.savefig(sys.argv[1] + '.aggr.pdf', bbox_inches='tight')
        plt.close()
    def _Dump(self):
        with open(sys.argv[1] + '.aggr.data', 'w') as f:
            f.write('{}'.format({str(k): v for k, v in self.data.items()}))

if __name__ == '__main__':
    d = Data(sys.argv[1])
    d.Plot()
    d._Dump()
