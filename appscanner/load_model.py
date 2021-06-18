import os
import pickle

models = []
# for model_indx in os.listdir('appscanner_models'):
#     print('Loading {}'.format(model_indx))
#     model_path = os.path.join('appscanner_models', model_indx, 'model')

#     with open(model_path, 'rb') as f:
#         model = pickle.load(f)
    
#     models.append(model)

#     print('...............DONE...............\n')

li = ['among_us', 'animal_restaurant', 'azar', 'baohay24h', 'baomoi', 'bbc_news', 
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

print(len(li))