import json
from sklearn.metrics import classification_report
import os

predictions = []
labels = []

for filename in os.listdir('predictions/model_1'):
    path = os.path.join('predictions/model_1', filename)
    with open(path, 'r') as fp:
        data = json.load(fp)
    predictions = predictions + data['predictions']
    labels = labels + data['labels']

    print(filename)
    # print(len(data['predictions']))
    # print(data['predictions'])
    # print(len(data['labels']))
    # print(data['labels'])
    print('----------------')

print(len(predictions))
print(len(labels))
print(classification_report(labels, predictions))

