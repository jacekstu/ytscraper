from scraper import Scraper

channels_lt = [{"channel":'UCD8OLqfxtRU7aUsezbPSe6w', "isLegacy":False}]

scraper_obj = Scraper('API_KEY')

# Get  only username works correctly
# Two methods are needed, you have to make sure that the channel has a legacy name, and the use forUsername
# if the legacy name is not defined then you need to use the channel's id.

playlist_id = scraper_obj.get_playlist_id(channels_lt[0]) 
videos = scraper_obj.get_videos(playlist_id)

for vid in videos:
	print(vid)

print(len(videos))