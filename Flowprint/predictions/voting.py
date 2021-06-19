import os
import json
from collections import Counter

model_set = 'models_T1_t10'

apps = dict()

models = os.listdir(model_set)
# add model_set before
models = [os.path.join(model_set, x) for x in models]

for model in models:
    for filename in os.listdir(model):
        json_path = os.path.join(model, filename)
        with open(json_path, 'r') as f:
            data = json.load(f)
            preds = data['predictions']
        if filename not in apps.keys():
            apps[filename] = [preds]
        else:
            apps[filename].append(preds)


print(apps.keys())
votings = dict()
for k in apps.keys():
    app_name = k.split('.')[0]
    data = apps[k]
    
    models_num = len(data)
    samples_num = len(data[0])
    li = [[]]*samples_num
    for x in data:
        for i in range(samples_num):
            li[i] = li[i] + [x[i]]
    
    voting_li = [Counter(y).most_common(1)[0][0] for y in li]
    votings[k] = {'predictions': voting_li, 'labels': [app_name]*len(voting_li)}
    
# save into voting
for k in votings.keys():
    data = votings[k]
    saved_path = os.path.join(model_set, 'voting', k)
    print(saved_path)
    with open(saved_path, 'w') as f:
        json.dump(data, f)