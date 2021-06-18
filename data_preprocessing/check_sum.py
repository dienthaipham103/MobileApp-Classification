import os
import pandas as pd
import sys

args = sys.argv
app = args[1:][0]

print(app)
s = 0
app_path = os.path.join(app, 'csv')
for filename in os.listdir(app_path):
    print(filename)
    path = os.path.join(app_path, filename)
    
    df = pd.read_csv(path)
    start = df['time'].iloc[0]
    end = df['time'].iloc[-1]
    number = int(filename.split('_')[1])

    duration = round((end - start)/60/60, 2)
    s += duration*number

print('Total: ', s)