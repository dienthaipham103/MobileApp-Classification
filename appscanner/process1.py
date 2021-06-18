import argparse
import os
import sys
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from preprocessor import Preprocessor
from appscanner import AppScanner
import collections
import sys


def extract_labels(files):
    """Extract the labels as the directory in which the files reside."""
    # Initialise result
    result = list()
    # Loop over all files
    for file in files:
        # Extract directory name
        result.append(os.path.split(os.path.dirname(file))[-1])
    # Return result
    return result

def prediction_v1(one_app_prediction=True, apps=None):
    appscanner = AppScanner()
    # appscanner.fit_models(models_folder='appscanner_models')

    appscanner.load_models('appscanner_models')

    # predict one time
    # y_pred, y_test = appscanner.predict_test_dataset(path='test')
    # print(classification_report(y_test, y_pred))

    # predict each class seperately
    for app in apps:
        y_pred, y_test = appscanner.predict_one_app(app)

def prediction_v2(one_app_prediction=True, apps=None):
    appscanner = AppScanner()
    # appscanner.fit_models(models_folder='appscanner_models')

    appscanner.load_one_model('appscanner_models/model_15/model')

    # predict each class seperately
    for app in apps:
        y_pred, y_test = appscanner.predict_one_app(app, prediction_folder='predictions/model_15', multiple=False)


if __name__ == "__main__":
    app_list = ['among_us', 'animal_restaurant', 'azar', 'baohay24h', 'baomoi', 'bbc_news', 
            'bida', 'bigo', 'cake', 'chess', 'cho_tot', 'cnn_news', 'comico', 'co_tuong_online', 
            'dan_tri', 'diijam', 'dubsmash', 'facebook', 'fptplay', 'freefire', 'google_meet',  
            'hahalolo', 'hello_yo', 'instagram', 'iQIYI', 'jobway', 'kaka', 'kenh14', 'lazada', 
            'lienquan_mobile', 'likee_lite', 'linkedin', 'lotus', 'mangatoon', 'may', 'medoctruyen',
            'messenger', 'mobile_legend', 'myradio', 'netflix', 'nhaccuatui', 'nhacvang', 'nimotv', 
            'nonolive', 'noveltoon', 'ola_party', 'partying', 'phim247', 'pinterest', 'podcast_player',
            'popskid', 'pubg', 'quora', 'radiofm', 'reddit', 'sachnoiapp', 'sendo', 'shopee', 'skype', 
            'snapchat', 'soha', 'soundcloud', 'spotify', 'starmarker', 'tango', 'ted', 'telegram', 
            'thanhnien', 'the_guardian', 'tien_len', 'tiki', 'tiktok', 'tinder', 'tinhte', 'tinmoi24h',
            'tivi247', 'tivi24h', 'tivi360', 'tivi_truyentranh_webtoon', 'toc_chien', 'topcv',
            'truyenaudio', 'truyenaudiosachnoiviet', 'tunefm', 'tuoitre_online', 'twitch', 'twitter',
            'vieon', 'vietnamworks', 'vnexpress', 'voizfm', 'vtvgo', 'zoom', 'hago',
            'wallstreet_journal', 'weeboo', 'wesing', 'wetv', 'wikipedia', 'zalo', 'zingmp3']
    prediction_v2(one_app_prediction=True, apps=app_list)
    

    


