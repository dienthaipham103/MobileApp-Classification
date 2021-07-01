import json
import os

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

models = ['model_1', 'model_2', 'model_3', 'model_4', 'model_5', 'model_6', 'model_16']

app_counts = dict()

for model in models:
	for filename in os.listdir(model):
		json_path = os.path.join(model, filename)
		with open(json_path, 'r') as f:
			data = json.load(f)
		pred_len = len(data['predictions'])
		label_len = len(data['labels'])
		if pred_len != label_len:
			raise Exception('Error! .......................................')
		
		if filename not in app_counts.keys():
			app_counts[filename] = pred_len
		else:
			if app_counts[filename] != pred_len:
				raise Exception('Error! .......................................')

print(app_counts)
print('................................OK...................................')