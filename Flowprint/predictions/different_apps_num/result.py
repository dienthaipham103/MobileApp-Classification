import json
from operator import add
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score
import os
from statistics import stdev
import warnings
warnings.filterwarnings("ignore")


model_set = '90'

apps = dict()
models = os.listdir(model_set)
# models = ['5_models_voting', '10_models_voting', '15_models_voting', '20_models_voting', '25_models_voting',
#             '30_models_voting', '35_models_voting', '40_models_voting', '45_models_voting', '50_models_voting',
#             '55_models_voting', '60_models_voting', '65_models_voting', '70_models_voting', '75_models_voting',
#             '80_models_voting', '85_models_voting', '90_models_voting', '95_models_voting', 'voting'
# ]
models = [os.path.join(model_set, x) for x in models]

precision_li = []
recall_li = []
f1_li = []
acc_li = []

best_model = {'precision': 0, 'recall': 0, 'f1-score': 0, 'accuracy': 0}
worst_model = {'precision': 100, 'recall': 100, 'f1-score': 100, 'accuracy': 100}

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

    # save to best score
    if f1 > best_model['f1-score'] and model != os.path.join(model_set, 'voting'):
        best_model['precision'] = precision
        best_model['recall'] = recall
        best_model['f1-score'] = f1
        best_model['accuracy'] = acc
    
    # save to worst model
    if f1 < worst_model['f1-score']:
        worst_model['precision'] = precision
        worst_model['recall'] = recall
        worst_model['f1-score'] = f1
        worst_model['accuracy'] = acc

    # print(classification_report(labels, predictions, digits=4))
    print('pre: ', precision)
    print('recall: ', recall)
    print('f1: ', f1)
    print('acc: ', acc)
    print('...........................................')

    # add to list
    if model != 'voting':
        precision_li.append(precision)
        recall_li.append(recall)
        f1_li.append(f1)
        acc_li.append(acc)
    
print(len(precision_li))

# mean
print('Mean')
print('precision mean: ', sum(precision_li)/100)
print('recall mean: ', sum(recall_li)/100)
print('f1 mean: ', sum(f1_li)/100)
print('acc mean: ', sum(acc_li)/100)
print('........................................................')

# std
print('Standard deviation')
print('precision std: ', stdev(precision_li))
print('recall std: ', stdev(recall_li))
print('f1 std: ', stdev(f1_li))
print('acc std: ', stdev(acc_li))
print('........................................................')

print('........................................................')
print('Best model')
print('pre: ', best_model['precision'])
print('recall: ', best_model['recall'])
print('f1: ', best_model['f1-score'])
print('acc: ', best_model['accuracy'])
print('.........................................................')

print('Worst model')
print('pre: ', worst_model['precision'])
print('recall: ', worst_model['recall'])
print('f1: ', worst_model['f1-score'])
print('acc: ', worst_model['accuracy'])
print('.........................................................')


