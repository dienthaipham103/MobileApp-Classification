from cryptography import x509
from cryptography.hazmat.backends import default_backend
import glob
import numpy as np
import os
import pyshark
import re
import warnings
from subprocess import Popen, PIPE
import pandas as pd
import sys

args = sys.argv
app_name = args[1]


def tshark_version():
    """Returns the current version of tshark.

        Returns
        -------
        version : string
            Current version number of tshark.
        """
    # Get tshark version via command line
    command = ["tshark", "--version"]
    process = Popen(command, stdout=PIPE, stderr=PIPE)
    out, err = process.communicate()

    # Throw error if any
    if err:
        raise ValueError(
            "Exception in tshark version check: '{}'".format(err))

    # Search for version number
    regex = re.compile('TShark .*(\d+\.\d+\.\d+) ')
    out = out.decode('utf-8')
    version = regex.search(out).group(1)

    # Return version
    return version


# Get tshark version
version = tshark_version()
# Set certificate command based on version
# tshark versions <3 use ssl.handshake.certificate
# tshark versions 3+ use tls.handshake.certificate
certificate = "ssl" if int(version.split('.')[0]) < 3 else "tls"
certificate += ".handshake.certificate"

################################# loop over all files ##############################################
# app_name = "bigo"
# app_name = "youtube"
# app_name = "zing_mp3"
exist_files = [x[:-4] for x in os.listdir(app_name + "/csv")]
count = 0
for filename in os.listdir(app_name + "/pcap"):
    if filename[:-5] not in exist_files:
        count += 1
        print('file: -------------------------------------------------', count)
        path = os.path.join(app_name + "/pcap", filename)
        saved_path = os.path.join(app_name + "/csv", filename[:-4] + 'csv')

        # Create Tshark command
        command = ["tshark", "-r", path, "-Tfields",
                "-e", "frame.time_epoch",
                "-e", "tcp.stream",
                "-e", "udp.stream",
                "-e", "ip.proto",
                "-e", "ip.src",
                "-e", "tcp.srcport",
                "-e", "udp.srcport",
                "-e", "ip.dst",
                "-e", "tcp.dstport",
                "-e", "udp.dstport",
                "-e", "ip.len",
                "-e", certificate]
        # Initialise result
        result = list()

        # Call Tshark on packets
        process = Popen(command, stdout=PIPE, stderr=PIPE)
        # Get output
        out, err = process.communicate()

        # Give warning message if any
        if err:
            warnings.warn("Error reading file: '{}'".format(
                err.decode('utf-8')))

        count = 0
        # Read each packet
        for packet in filter(None, out.decode('utf-8').split('\n')):
            # Get all data from packets
            packet = packet.split()

            # Perform check on packets
            if len(packet) < 8:
                continue

            # Perform check on multiple ip addresses
            packet[3] = packet[3].split(',')[0]
            packet[5] = packet[5].split(',')[0]
            packet[7] = packet[7].replace(',', '')

            # Parse certificate
            if len(packet) > 8:
                # Get first certificate
                cert = packet[8].split(',')[0]
                # Transform to hex
                cert = bytes.fromhex(cert.replace(':', ''))
                # Read as certificate
                cert = x509.load_der_x509_certificate(cert, default_backend())
                # Set packet as serial number
                packet[8] = cert.serial_number
            else:
                packet.append(None)

            count += 1
            print(count)

            # Add packet to result
            result.append(packet)

        # Get result as numpy array
        result = np.asarray(result)

        # Check if any items exist
        # if not result.shape[0]:
        #     return np.zeros((0, 8), dtype=object)

        # Change protocol number to text
        protocols = {'17': 'udp', '6': 'tcp'}
        result[:, 2] = [protocols.get(x, 'unknown') for x in result[:, 2]]


        # get the base timestamp
        base = float(result[0][0])

        df = pd.DataFrame(result, 
                            columns=['time', 'stream_id', 'protocol',
                                    'source_address', 'source_port', 
                                    'destination_address', 'destination_port', 
                                    'length', 'certificate'])
        df['time'] = pd.to_numeric(df['time']) - base
        df['time'][0] = 0
        df['length'] = pd.to_numeric(df['length'])

        # save the dataframe into csv file
        df.to_csv(saved_path)


####################################################################################################