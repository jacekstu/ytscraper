from scraper import Scraper
filename = "scraping_list.txt"
import json

scraper_obj = Scraper('API_KEY')

channels_lt = []

json_file = open("scraping_list.txt", "r", encoding="utf-8")
channels = json.load(json_file)
json_file.close()

for channel in channels['channels']:
	channels_lt.append(channel)
	

for idx, channel in enumerate(channels_lt):
	playlist_id = scraper_obj.get_playlist_id(channels_lt[idx])
	videos = scraper_obj.get_videos(playlist_id)
	for vid in videos:
		print(vid.get('video_title'))
		#coms = scraper_obj.scrape_comments(vid.get('video_identificator'),vid.get('video_title') )




#channels_lt = [{"channel":'UCD8OLqfxtRU7aUsezbPSe6w', "isLegacy":False}]



# Get  only username works correctly
# Two methods are needed, you have to make sure that the channel has a legacy name, and the use forUsername
# if the legacy name is not defined then you need to use the channel's id.

#playlist_id = scraper_obj.get_playlist_id(channels_lt[0]) 
#videos = scraper_obj.get_videos(playlist_id)


#for vid in videos:
#	coms = scraper_obj.scrape_comments(vid.get('video_identificator'),vid.get('video_title') )

#coms =  scraper_obj.scrape_comments(videos[90].get('video_identificator'), videos[90].get('video_title'))
