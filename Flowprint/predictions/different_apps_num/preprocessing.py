import os
import json

model_sets = ['10', '20', '30', '40', '50', '60', '70', '80', '90']
for model_set in model_sets:
    count = 0
    for model in os.listdir(model_set):
        count += 1
        print(count)
        model_path = os.path.join(model_set, model)
        for filename in os.listdir(model_path):
            app = filename.split('.')[0]
            path = os.path.join(model_path, filename)
            with open(path, 'r+') as f:
                data = json.load(f)
                data['labels'] = [app]*len(data['predictions'])
                f.seek(0)
                json.dump(data, f)
                f.truncate()
    print('----------------------------------------------------------------------\n')