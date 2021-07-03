import warnings
warnings.filterwarnings("ignore")

from flowprint.flowprint     import FlowPrint
from flowprint.flow_generator import FlowGenerator
from sklearn.metrics         import classification_report

import os
import pandas as pd
import numpy as np
import json


from multiprocessing import Pool
from multiprocessing import current_process
from multiprocessing import cpu_count


NUMBER_OF_PROCESSED = cpu_count()
SAVE_MODELS_PATH = 'C:/Users/hothi/Desktop/Dien/9_classes_models/T5_t10'
TRAIN_DATA_PATH = 'C:/Users/hothi/Desktop/Dien/train_data_9_classes/T5'

with open('9_classes.json') as f:
    CLASSES = json.load(f)



def create_model(data_path, apps_to_train):

    apps_list = os.listdir(data_path)

    apps_list = [_ for _ in apps_list if '_'.join(_.split('_')[:-2]) in apps_to_train]
    # apps_list = [_ for _ in apps_list]

    # print(f'[PROCESS {current_process().name}]\t< INFO > : apps_to_train: {apps_to_train}'.expandtabs(3))
    print(f'[PROCESS {current_process().name}]\t< INFO > : apps_list: {apps_list}'.expandtabs(3))
    # print(f'[PROCESS {current_process().name}]\t< INFO > : apps_list__: {["_".join(_.split("_")[-2]) for _ in apps_list]}'.expandtabs(3))

    X, y = list(), list()

    for app in apps_list:
        app_data = pd.read_csv(f'{data_path}/{app}', index_col=0)
        app_data['app'] = app
        app_data = app_data[['app', 'protocol', 'stream_id', 'time', 'length', 'source_address', 'destination_address', 'source_port', 'destination_port', 'certificate']]
        app_data = app_data.where(pd.notnull(app_data), None)
        app_data = app_data.where(app_data != '', None)
        app_data = app_data[app_data.protocol != 'unknown']
        data = np.array(list(FlowGenerator().combine(app_data.values.astype('object')).values()))
        X.append(data)
        y.append(np.array([app] * data.shape[0]))

    X = list(filter(lambda x: x.shape[0] != 0, X))
    y = list(filter(lambda x: x.shape[0] != 0, y))
    try:
        X = np.concatenate(X)
        y = np.concatenate(y)
    except Exception:
        X = np.array([], dtype=object)
        y = np.array([], dtype=object)
    
    flowprint = FlowPrint(
        batch       = 300,
        window      = 10,
        correlation = 0.1,
        similarity  = 0.9
    )

    return flowprint.fit(X, y)


class KeyboardInterruptError(Exception): pass

def train_models(model_name):
    try:
        for class_name, apps_to_train in CLASSES.items():
            if not os.path.exists(f'{SAVE_MODELS_PATH}/{class_name}'):
                os.makedirs(f'{SAVE_MODELS_PATH}/{class_name}')

            save_path = f'{SAVE_MODELS_PATH}/{class_name}/{model_name.split("_")[-1]}.model'
            if os.path.isfile(save_path):
                print(f'[PROCESS {current_process().name}]\t< PASS > : Model {model_name.split("_")[-1]}\ttrained'.expandtabs(3))
                return

            model = create_model(f'{TRAIN_DATA_PATH}/{model_name}', apps_to_train)
            model.save(save_path)

            print(f'[PROCESS {current_process().name}]\t< DONE > : Model {model_name.split("_")[-1]}\ttrained'.expandtabs(3))
    except KeyboardInterrupt:
        raise KeyboardInterruptError()


if __name__ == '__main__':
    models_list = os.listdir(f'{TRAIN_DATA_PATH}')

    with Pool(NUMBER_OF_PROCESSED) as pool:
        print(f'NUMBER OF PROCESS {pool._processes}')

        try:
            pool.map(train_models, models_list)
        except KeyboardInterrupt:
            print('Caught KeyboardInterrupt, terminating workers')
            pool.terminate()
            pool.join()

    print('DONE!')
