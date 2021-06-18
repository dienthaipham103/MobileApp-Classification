import os
import shutil

for f in os.listdir('/CONVERT_NEW_DATA'):
    app_f = os.path.join('/CONVERT_NEW_DATA', f)
    if os.path.isdir(app_f):
        pcap_f = os.path.join(app_f, 'pcap')
        csv_f = os.path.join(app_f, 'csv')
        if not os.path.exists(pcap_f):
            os.mkdir(pcap_f)
            os.mkdir(csv_f)

            # copy file
            for filename in os.listdir(app_f):
                if not os.path.isdir(os.path.join(app_f, filename)):
                    p1 = os.path.join(app_f, filename)
                    p2 = os.path.join(pcap_f, filename)
                    shutil.move(p1, p2)
    
        print(f)
                