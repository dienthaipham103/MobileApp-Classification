import warnings
warnings.filterwarnings("ignore")

import os
import json
from load_csv import load_csv
from flowprint.flowprint     import FlowPrint
import numpy as np
import operator

import signal
from multiprocessing import Pool
from multiprocessing import current_process
from multiprocessing import cpu_count


TEST_DATA_PATH = 'C:/Users/hothi/Desktop/Dien/test_data/T5'
NUMBER_OF_PROCESSED = 12

with open('test_classed.json') as f:
    CLASSES = json.load(f)


def get_max_frequent(x):

    if len(x) == 0:
        return 'unknown_unknown'

    frequencies = {}
    for item in x:
        if item in frequencies:
            frequencies[item] += 1
        else:
            frequencies[item] = 1

    return max(frequencies.items(), key=operator.itemgetter(1))[0]


def predict(model_on_memory_file, app_sample):
    
    X, y = app_sample

    model = FlowPrint()
    model.load_on_memory_file(model_on_memory_file)
    fp_test = model.fingerprinter.fit_predict(X)
    y_pred = [list(_)[0] for _ in model.recognize(fp_test)]
    prediction = '_'.join(get_max_frequent(y_pred).split('_')[:-2])

    return prediction


def test_model_with_app(model, app_samples):
    predictions = []

    for app_sample in app_samples:
        prediction = predict(model, app_sample)
        predictions.append(prediction)

    return predictions

class KeyboardInterruptError(Exception): pass

def test_model(x):

    class_name, app_name = x

    MODEL_PATH = f'C:/Users/hothi/Desktop/Dien/9_classes_models/T5_t10/{class_name}'
    RESULT_FOLDER = f'C:/Users/hothi/Desktop/Dien/9_classes_predicts/T5_t10/{class_name}'

    try:
        app_samples_ = os.listdir(f'{TEST_DATA_PATH}/{app_name}')
        app_samples = []

        for app_sample_ in app_samples_:
            X, y = list(), list()

            app_path = f'{TEST_DATA_PATH}/{"_".join(app_sample_.split("_")[:-2])}/{app_sample_}'
            X_, y_ = load_csv(app_path, 'y')
            try:
                X = np.concatenate(X_)
                y = np.concatenate(y_)
            except Exception:
                X = np.array([], dtype=object)
                y = np.array([], dtype=object)
            
            app_samples.append((X, y))
        models_list = [_.split('.')[0] for _ in os.listdir(MODEL_PATH)]
        for model_name in models_list:
            if not os.path.exists(f'{RESULT_FOLDER}/{model_name}'):
                os.makedirs(f'{RESULT_FOLDER}/{model_name}')

            with open(f'{MODEL_PATH}/{model_name}.model', 'r') as model_file:
                model = json.load(model_file)

            result_file = f'{RESULT_FOLDER}/{model_name}/{app_name}.json'
            if os.path.isfile(result_file):
                print(f'[PROCESS {current_process().name}] < PASSED >: Model {model_name}\t{app_name}\talready predicted')
                continue

            predictions = test_model_with_app(model, app_samples)
            
            with open(result_file, 'w') as file:
                json.dump(
                    {
                        'predictions': predictions,
                    },
                    file,
                )
            
            print(f'[PROCESS {current_process().name}] < DONE >: Model {model_name}\t{app_name}')
    
    except KeyboardInterrupt:
        raise KeyboardInterruptError()


if __name__ == '__main__':

    for class_name, apps_list in CLASSES.items():

        print( '=============================================================')
        print(f'=========             START TESTING {class_name}              =========')
        print( '=============================================================')

        
        # MODEL_PATH = f'C:/Users/hothi/Desktop/Dien/9_classes_models/T5_t10/{class_name}'
        # RESULT_FOLDER = f'C:/Users/hothi/Desktop/Dien/9_classes_predicts/T5_t10/{class_name}'

        with Pool(NUMBER_OF_PROCESSED) as pool:
            print(f'NUMBER OF PROCESS {pool._processes}')

            try:
                pool.map(test_model, [(class_name, app_name) for app_name in apps_list])
            except KeyboardInterrupt:
                print('Caught KeyboardInterrupt, terminating workers')
                pool.terminate()
                pool.join()

        print( '=============================================================')
        print(f'=========              DONE TESTING {class_name}               =========')
        print( '=============================================================')