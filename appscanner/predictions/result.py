import json
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score
import os
from statistics import stdev
import warnings
warnings.filterwarnings("ignore")

models = ['model_1', 'model_2', 'model_3', 'model_4', 'model_5', 'model_6', 
            'model_7', 'model_8', 'model_9', 'model_10', 'model_11',
            'model_12', 'model_13', 'model_14', 'model_15', 'model_16', 'model_17'
        ]

precision_li = []
recall_li = []
f1_li = []
acc_li = []

for model in models:
    print(model)
    predictions = []
    labels = []

    for filename in os.listdir(model):
        path = os.path.join(model, filename)
        with open(path, 'r') as fp:
            data = json.load(fp)
        predictions = predictions + data['predictions']
        labels = labels + data['labels']

    precision = precision_score(labels, predictions, average='weighted')
    recall = recall_score(labels, predictions, average='weighted')
    f1 = f1_score(labels, predictions, average='weighted')
    acc = accuracy_score(labels, predictions)

    # print(classification_report(labels, predictions, digits=4))
    print('pre: ', precision)
    print('recall: ', recall)
    print('f1: ', f1)
    print('acc: ', acc)
    print('...........................................')

    # add to list
    if model != 'model_17':
        precision_li.append(precision)
        recall_li.append(recall)
        f1_li.append(f1)
        acc_li.append(acc)
    
print(len(precision_li))

# mean
print('precision mean: ', sum(precision_li)/16)
print('recall mean: ', sum(recall_li)/16)
print('f1 mean: ', sum(f1_li)/16)
print('acc mean: ', sum(acc_li)/16)

# std
print('precision std: ', stdev(precision_li))
print('recall std: ', stdev(recall_li))
print('f1 std: ', stdev(f1_li))
print('acc std: ', stdev(acc_li))

