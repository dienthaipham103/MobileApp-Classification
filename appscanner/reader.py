from scapy.all import *
import numpy as np
import ipaddress
import pandas as pd

#
from burst import Burst
from flow import Flow
from features import Features
#  

#
from cryptography import x509
from cryptography.hazmat.backends import default_backend
import glob
import os
import re
import warnings
from subprocess import Popen, PIPE
#

class Reader(object):

    def __init__(self, verbose=False):
        """Reader object for reading packets from .pcap files.

            Parameters
            ----------
            verbose : boolean, default=false
                If True, print which files are being read.
            """
        self.verbose = verbose
    
    def tshark_version(self):
        """Returns the current version of tshark.
            Returns
            -------
            version : string
                Current version number of tshark.
            """
        # Get tshark version via command line
        command  = ["tshark", "--version"]
        process  = Popen(command, stdout=PIPE, stderr=PIPE)
        out, err = process.communicate()

        # Throw error if any
        if err:
            raise ValueError(
                "Exception in tshark version check: '{}'".format(err))

        # Search for version number
        regex   = re.compile('TShark .*(\d+\.\d+\.\d+) ')
        out     = out.decode('utf-8')
        version = regex.search(out).group(1)

        # Return version
        return version
    
    """
        created by dienthaipham
    """
    def basic_reprocessing(self, df):
        df = df[df['protocol'] != 'unknown']

        # remove dns protocol
        df = df[(df['source_port'] != 53) & (df['destination_port'] != 53) & 
                (df['source_port'] != 5353) & (df['destination_port'] != 5353) &
                (df['source_port'] != 137) & (df['destination_port'] != 137) &
                (df['source_port'] != 67) & (df['destination_port'] != 67) &
                (df['source_port'] != 68) & (df['destination_port'] != 68) &
                (df['source_port'] != 5355) & (df['destination_port'] != 5355)]
        
        # remove IP 239.255.255.250, protocol SSDP
        df = df[(df['source_address'] != '239.255.255.250') & (df['destination_address'] != '239.255.255.250')]

        return df

    """
        created by dienthaipham
    """
    def read_csv(self, path):
        # print('Loading {} ...'.format(path))
        df = pd.read_csv(path, index_col=0)
        df = self.basic_reprocessing(df)


        df = df[['time', 'source_address', 'destination_address', 'source_port', 'destination_port', 'length']]
        df['time'] = df['time'].apply(lambda x: EDecimal(x))
        df['source_address'] = df['source_address'].apply(lambda x: int(ipaddress.ip_address(x.split(',')[0])))
        df['destination_address'] = df['destination_address'].apply(lambda x: int(ipaddress.ip_address(x.split(',')[0])))


        self.packets = np.array(df, dtype=object)

        return self.packets

    """
        created by dienthaipham
    """
    def read_tshark(self, path):
        """Read TCP and UDP packets from file given by path using tshark backend
            Parameters
            ----------
            path : string
                Path to .pcap file to read.
            Returns
            -------
            result : np.array of shape=(n_packets, n_features)
                Where features consist of:
                0) Timestamp of packet
                1) IP packet source
                2) IP packet destination
                3) TCP/UDP packet source port
                4) TCP/UDP packet destination port
                5) Length of packet
            """
        # Get tshark version
        version = self.tshark_version()
        # Set certificate command based on version
        # tshark versions <3 use ssl.handshake.certificate
        # tshark versions 3+ use tls.handshake.certificate
        certificate  = "ssl" if int(version.split('.')[0]) < 3 else "tls"
        certificate += ".handshake.certificate"

        # Create Tshark command
        command = ["tshark", "-r", path, "-Tfields",
                   "-e", "frame.time_epoch",
                   "-e", "ip.src",
                   "-e", "ip.dst",
                   "-e", "tcp.srcport",
                   "-e", "udp.srcport",
                   "-e", "tcp.dstport",
                   "-e", "udp.dstport",
                   "-e", "ip.len",
                   ]
        # Initialise result
        result = []

        # Call Tshark on packets
        process = Popen(command, stdout=PIPE, stderr=PIPE)
        # Get output
        out, err = process.communicate()

        # Give warning message if any
        if err:
            warnings.warn("Error reading file: '{}'".format(
                err.decode('utf-8')))

        # Read each packet
        for packet in filter(None, out.decode('utf-8').split('\n')):
            # Get all data from packets
            packet = packet.split()

            # Perform check on packets
            if len(packet) < 5: 
                continue

            # Perform check on multiple ip addresses
            packet[1] =  int(ipaddress.ip_address(packet[1].split(',')[0]))
            packet[2] =  int(ipaddress.ip_address(packet[2].split(',')[0]))
            packet[5] = packet[5].replace(',', '')


            # Add packet to result
            result.append([EDecimal(packet[0]), int(packet[1]), int(packet[2]), int(packet[3]), int(packet[4]), int(packet[5])])

        # Get result as numpy array
        self.packets = np.array(result, dtype=object)

        # Check if any items exist
        if not self.packets.shape[0]:
            return np.zeros((0, 5), dtype=object)


        return self.packets

    def read(self, infile):
        """Read TCP packets from input file.
            Parameters
            ----------
            infile : string
                pcap file from which to read packets.
            Returns
            -------
            result : list
                List of packets extracted from pcap file.
                Each packet is represented as a list of:
                 - timestamp
                 - IP source (in byte representation)
                 - IP destination (in byte representation)
                 - TCP source port
                 - TCP destination port
                 - packet length.
            """
        # If verbose, print loading file
        if self.verbose:
            print("Loading {}...".format(infile))

        # Set buffer of packets
        self.packets = []
        # Process packets in infile
        sniff(prn=self.extract, lfilter=lambda x: TCP in x, offline=infile)

        # Convert to numpy array
        self.packets = np.array(self.packets)
        # In case of packets, sort on timestamp
        if self.packets.shape[0]:
            # Sort based on timestamp
            self.packets = self.packets[self.packets[:, 0].argsort()]

        # Return extracted packets
        return self.packets


    def extract(self, packet):
        """Extract relevant fields from given packet and adds it to globel
           self.packets variable.

            Parameters
            ----------
            packet : scapy.IP
                Scapy IP packet extracted by sniff function.
            """
        # Extract relevant content from packet
        data = [packet.time,
                int(ipaddress.ip_address(packet["IP"].src)),
                int(ipaddress.ip_address(packet["IP"].dst)),
                packet["TCP"].sport,
                packet["TCP"].dport,
                packet["IP"].len]
        # Add packet to buffer
        self.packets.append(data)

if __name__ == "__main__":
    print('====================Check=========================')

    # define reader object
    reader_obj = Reader()
    burst_obj = Burst()
    flow_obj = Flow()
    feature_obj = Features()


    # file_list = ['test_data/zing_mp3.pcap']
    file_list = ['test_data//zing_mp3.csv']

    for path in file_list:
        # packets = reader_obj.read_tshark(path)
        # packets = reader_obj.read(path)
        packets = reader_obj.read_csv(path)
        # print(packets)
        # print(packets.shape)
        

        bursts = burst_obj.split(packets, 1)
        # print(bursts)

        flows = flow_obj.extract(bursts)
        # print(flows)

        features = feature_obj.extract(flows)
        print(features)

        
    

######################################################################################################
# reader.py
# read_csv
# output:

# [[Decimal('0.0159237384796142578125') 3232270663 836072087 42054 443 60]
#  [Decimal('0.023298740386962890625') 836072087 3232270663 443 42054 60]
#  [Decimal('0.0282530784606933628444469519536141888238489627838134765625')
#   3232270663 836072087 42054 443 52]
#  ...
#  [Decimal('3621.6034667491912841796875') 985335813 3232270663 443 54061
#   52]
#  [Decimal('3621.810349941253662109375') 3232270663 3741282829 52012 443
#   52]
#  [Decimal('3621.8129708766937255859375') 3232270663 985335813 54061 443
#   52]]
# (116862, 6)

# -----------------------------------------------------------------------------------------------------

# burst.py
# split
# input: packets
# output:

# [
# array([[Decimal('3261.9669082164764404296875'), 3741309060, 3232270663,
#         80, 33857, 52],
#        [Decimal('3262.081050872802734375'), 3232270663, 3741309060,
#         33857, 80, 52]], dtype=object), 
# array([[Decimal('3265.1483938694000244140625'), 3741309096, 3232270663,
#         80, 57582, 52],
#        [Decimal('3265.4613049030303955078125'), 3232270663, 3741309096,
#         57582, 80, 52]], dtype=object), 
# array([[Decimal('3268.6157219409942626953125'), 1730632708, 3232270663,
#         443, 60383, 52],
#        [Decimal('3268.840953826904296875'), 3232270663, 1730632708,
#         60383, 443, 52]], dtype=object), 
# array([[Decimal('3270.1400737762451171875'), 1249758396, 3232270663,
#         5228, 50154, 76],
#        [Decimal('3270.380240917205810546875'), 3232270663, 1249758396,
#         50154, 5228, 80],
#        [Decimal('3270.4552299976348876953125'), 1249758396, 3232270663,
#         5228, 50154, 52]], dtype=object), 
# array([[Decimal('3273.168079853057861328125'), 2899947214, 3232270663,
#         443, 45423, 52],
#        [Decimal('3273.4125869274139404296875'), 2899947214, 3232270663,
#         443, 45423, 52],
#        [Decimal('3273.4489269256591796875'), 3232270663, 2899947214,
#         45423, 443, 64],
#        [Decimal('3274.123591899871826171875'), 3741309090, 3232270663,
#         80, 56742, 52],
#        [Decimal('3274.3696029186248779296875'), 3232270663, 3741309090,
#         56742, 80, 52]], dtype=object)
# ]

# --------------------------------------------------------------------------------------------------
# flow.py
# extract
# input: bursts
# output:

# (3077.209352016449, '192.168.137.71', 56742, '222.255.216.162', 80): array([-52,  52]), 
# (3077.209352016449, '192.168.137.71', 54345, '172.217.24.74', 443): array([52, 52, 52, 52]), 
# (3077.209352016449, '192.168.137.71', 42992, '172.217.161.138', 443): array([52, 52, 52, 52]), 
# (3077.209352016449, '192.168.137.71', 39645, '216.58.197.106', 443): array([60, -60, 52, 569, -52, -1470, -1470, -308, 52,
# 52, 52, 252, -52, 1073,   -52,  -430, -1470,  -153, -79,    52,    52,    52,    52])

# --------------------------------------------------------------------------------------------------
# features.py
# extract
# input: flows
# output:

# (3609.952954769135, '192.168.137.71', 58761, '120.138.69.227', 443): array([-1.49200000e+03, -5.20000000e+01, -6.58285714e+02,  4.76612245e+02,
#         6.12410732e+02,  3.75046905e+05, -6.88980671e-01, -1.27145484e+00,
#        -1.49200000e+03, -1.32540000e+03, -8.25600000e+02, -6.12600000e+02,
#        -5.43000000e+02, -4.03200000e+02, -2.60000000e+02, -1.10000000e+02,
#        -5.68000000e+01,  7.00000000e+00,  5.20000000e+01,  1.30700000e+03,
#         2.13500000e+02,  2.31600000e+02,  3.91750842e+02,  1.53468722e+05,
#         2.95438131e+00,  8.95329836e+00,  5.20000000e+01,  5.20000000e+01,
#         5.20000000e+01,  5.20000000e+01,  5.20000000e+01,  5.52000000e+01,
#         9.54000000e+01,  1.98000000e+02,  3.80900000e+02,  1.00000000e+01,
#        -1.49200000e+03,  1.30700000e+03, -1.45470588e+02,  4.43370242e+02,
#         6.50045875e+02,  4.22559640e+05, -4.78420748e-01,  2.04261314e+00,
#        -9.92200000e+02, -4.96400000e+02, -1.10000000e+02, -1.04000000e+01,
#         5.20000000e+01,  5.20000000e+01,  5.20000000e+01,  5.84000000e+01,
#         2.18000000e+02,  1.70000000e+01]), 
# (3609.952954769135, '192.168.137.71', 33563, '49.213.114.151', 443): array([-1.48000000e+03, -5.20000000e+01, -4.06600000e+02,  4.04293333e+02,
#         5.35393554e+02,  2.86646257e+05, -1.54017692e+00,  7.36601000e-01,
#        -1.40480000e+03, -5.59200000e+02, -3.08400000e+02, -2.72000000e+02,
#        -1.21000000e+02, -9.00000000e+01, -9.00000000e+01, -5.84000000e+01,
#        -5.20000000e+01,  1.50000000e+01,  5.20000000e+01,  8.05000000e+02,
#         1.56071429e+02,  1.54826531e+02,  2.32282144e+02,  5.39549945e+04,
#         2.38110457e+00,  4.88417233e+00,  5.20000000e+01,  5.20000000e+01,
#         5.20000000e+01,  5.20000000e+01,  5.20000000e+01,  5.20000000e+01,
#         6.45000000e+01,  1.34200000e+02,  4.51700000e+02,  1.40000000e+01,
#        -1.48000000e+03,  8.05000000e+02, -1.34965517e+02,  3.13602854e+02,
#         5.00252685e+02,  2.50252749e+05, -1.57765209e+00,  3.28953185e+00,
#        -5.59200000e+02, -2.72000000e+02, -9.00000000e+01, -5.84000000e+01,
#        -5.20000000e+01,  5.20000000e+01,  5.20000000e+01,  5.20000000e+01,
#         1.19600000e+02,  2.90000000e+01])

# --------------------------------------------------------------------------------------------------
