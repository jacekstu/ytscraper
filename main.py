from scraper import Scraper
filename = "scraping_list.txt"
import json
from file_handler import Handler


# 1 Create an object that stores the videos that have already been scraped
fh = Handler("scraped.txt")
scraped_videos = fh.get_scraped_videos()

# 2 Create a Scraper object, a class that stores all scraping code
scraper_obj = Scraper('API_KEY')

# 3 Create a list that will store the channels to scrape
channels_lt = []
json_file = open("scraping_list.txt", "r", encoding="utf-8")
channels = json.load(json_file)
json_file.close()

# 4 Read the data from json and add it to the list
for channel in channels['channels']:
	channels_lt.append(channel)
	
# 5 Iterate over channels, using indx 
for idx, channel in enumerate(channels_lt):
	# 6 Get the playlist of every channel in your channel list
	playlist_id = scraper_obj.get_playlist_id(channels_lt[idx])
	# 7 Get all the videos associated with a given channel
	videos = scraper_obj.get_videos(playlist_id)
	# 8 Scrape each video one at a time
	for vid in videos:
		# 9 check if list of scraped videos has this video a;ready scraped
		if str(vid.get('video_identificator')) in scraped_videos:
			print(vid, "This video has been scraped before")
		else:
			fh.write_to_scraped(str(vid.get('video_identificator')))
			coms = scraper_obj.scrape_comments(vid.get('video_identificator'),vid.get('video_title'))


# Get  only username works correctly
# Two methods are needed, you have to make sure that the channel has a legacy name, and the use forUsername
# if the legacy name is not defined then you need to use the channel's id.

#playlist_id = scraper_obj.get_playlist_id(channels_lt[0]) 
#videos = scraper_obj.get_videos(playlist_id)


#for vid in videos:
#	coms = scraper_obj.scrape_comments(vid.get('video_identificator'),vid.get('video_title') )

#coms =  scraper_obj.scrape_comments(videos[90].get('video_identificator'), videos[90].get('video_title'))
