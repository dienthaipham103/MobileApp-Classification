import sys
import re
import time
from cryptography import x509
from cryptography.hazmat.backends import default_backend
import numpy as np
import os
import re
import warnings
from subprocess import Popen, PIPE
import pandas as pd

import queue
from threading import Thread
from tqdm import tqdm

NUMBER_OF_THREADS = 4


def get_tshark_version():
    command = ["tshark", "--version"]
    process = Popen(command, stdout=PIPE, stderr=PIPE)
    out, err = process.communicate()

    if err:
        raise ValueError(
            "Exception in tshark version check: '{}'".format(err))

    regex = re.compile('TShark .*(\d+\.\d+\.\d+) ')
    out = out.decode('utf-8')
    version = regex.search(out).group(1)

    return version


version      = get_tshark_version()
certificate  = "ssl" if int(version.split('.')[0]) < 3 else "tls"
certificate += ".handshake.certificate"



class Worker(Thread):

    def __init__(self, function, tasks_queue, thread_name):
        super().__init__()
        self.function    = function
        self.tasks_queue = tasks_queue
        self.thread_name = thread_name


    def run(self):
        while True:
            try:
                task = self.tasks_queue.get(timeout=3)
                self.function(task, self.thread_name)
            except queue.Empty:
                tqdm.write(f'[THREAD {self.thread_name}]:\tDONE')
                return



class FileInput:

    def __init__(self, app, file_name):
        self.app        = app
        self.file_name  = file_name



def process_file(task, thread_name):
    index        = task[0]
    file_input   = task[1]
    save_path    = os.path.join(file_input.app + "/csv", file_input.file_name[:-4] + 'csv')
    file_to_read = os.path.join(file_input.app + "/pcap", file_input.file_name)

    progress_bar = tqdm(desc=f'[Thread {thread_name}]:\t[Index {index}]\tProcessing File {file_input.file_name}')

    command = ["tshark", "-r", file_to_read, "-Tfields",
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

    tshark_process = Popen(command, stdout=PIPE, stderr=PIPE)

    out_file = open(save_path + '.incompleted', 'w')
    out_file.write(',time,stream_id,protocol,source_address,source_port,destination_address,destination_port,length,certificate\n')

    protocols = {'17': 'udp', '6': 'tcp'}

    # time_base   = 0.0
    # first_time  = True
    count       = -1
    with tshark_process.stdout:
        for line in iter(tshark_process.stdout.readline, b''):
            packet_data = line.decode("utf-8").split()

            # Perform check on packets
            if len(packet_data) < 8:
                continue
            
            # if first_time:
            #     first_time = False
            #     time_base  = float(packet_data[0])
            
            # packet_data[0] = float(packet_data[0]) - time_base
            packet_data[0] = float(packet_data[0])

            packet_data[2] = protocols.get(packet_data[2], 'unknown')

            # Perform check on multiple ip addresses
            packet_data[3] = packet_data[3].split(',')[0]
            packet_data[5] = packet_data[5].split(',')[0]
            packet_data[7] = packet_data[7].replace(',', '')

            # Parse certificate
            if len(packet_data) > 8:
                cert = packet_data[8].split(',')[0]
                cert = bytes.fromhex(cert.replace(':', ''))
                cert = x509.load_der_x509_certificate(cert, default_backend())
                packet_data[8] = cert.serial_number
            else:
                packet_data.append('')

            
            count += 1
            out_file.write(','.join(map(str, [count, *packet_data]))+'\n')
            progress_bar.update()
    

    out_file.close()

    os.rename(save_path + '.incompleted', save_path)

    # result = np.asarray(result)

    # # Change protocol number to text
    # protocols = {'17': 'udp', '6': 'tcp'}
    # result[:, 2] = [protocols.get(x, 'unknown') for x in result[:, 2]]


    # # get the base timestamp
    # base = float(result[0][0])

    # df = pd.DataFrame(result, 
    #                     columns=['time', 'stream_id', 'protocol',
    #                             'source_address', 'source_port', 
    #                             'destination_address', 'destination_port', 
    #                             'length', 'certificate'])
    # result = None
    # df['time'] = pd.to_numeric(df['time']) - base
    # df['time'][0] = 0
    # df['length'] = pd.to_numeric(df['length'])

    # # save the dataframe into csv file
    # df.to_csv(save_path)



def main(apps):
    pcap_files = []
    csv_files  = []
    for app in apps:
        pcap_files.extend(map(lambda file_name: FileInput(app, file_name), os.listdir(app + "/pcap")))
        csv_files.extend(map(lambda file_name: file_name[:-4], os.listdir(app + "/csv")))

    files_to_process    = list(filter(lambda pcap_files: pcap_files.file_name[:-5] not in csv_files, pcap_files))

    tqdm.write(f'TOTAL NUMBER OF FILES TO PROCESS: {len(files_to_process)}')
    tasks_queue         = queue.Queue()
    tasks_queue.queue   = queue.deque(list(enumerate(files_to_process)))
    workers             = [Worker(process_file, tasks_queue, _) for _ in range(NUMBER_OF_THREADS)]

    for worker in workers:
        worker.start()

    for worker in workers:
        worker.join()
    
    tqdm.write('[ALL THREAD]: DONE')


if __name__ == '__main__':
    args = sys.argv
    apps = args[1:]
    main(apps)
