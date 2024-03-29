from scraper import Scraper
filename = "scraping_list.txt"
import json
from file_handler import Handler
from googleapiclient.errors import HttpError
import sys

# flag keeping track of errors
isError = False
# Errors
HTTP_403_COMMENTS_DISABLED = "parameter has disabled comments"
HTTP_404_NOT_FOUND = "parameter could not be found."
HTTP_404_CANNOT_BE_FOUND = "parameter cannot be found."
HTTP_403_QUOTA_EXCEEDED = "cannot be completed because you have exceeded"

# 1 Create an object that stores the videos that have already been scraped
fh = Handler("scraped.txt")
scraped_videos = fh.get_scraped_videos()

# 2 Create a Scraper object, a class that stores all scraping code
scraper_obj = Scraper('API_KEY', "http://localhost:8080/api/")

# 3 Create a list that will store the channels to scrape
channels_lt = []
json_file = open("scraping_list.txt", "r", encoding="utf-8")
channels = json.load(json_file)
json_file.close()

# 4 Read the data from json and add it to the list
# Also populate the channels with their display names, here it will be the cheapest (the least amount of quota)
for channel in channels['channels']:
	if not channel['isLegacy']:
		channel['name'] = scraper_obj.get_channel_name(channel['channel'])
	channels_lt.append(channel)
	

# 5 Iterate over channels, using indx 
print("INFO: Getting playlist from each channel")
for idx, channel in enumerate(channels_lt):
	# 6 Get the playlist of every channel in your channel list
	playlist_id  = scraper_obj.get_playlist_id(channels_lt[idx])
	# 7 Get all the videos associated with a given channel
	videos = scraper_obj.get_videos(playlist_id, channel)
print("INFO: Done adding channels' playlists")

# 8 Scrape each video one at a time
print("INFO: Proceeding to scraping videos")
for vid in videos:
	# 9 check if list of scraped videos has this video already scraped
	if str(vid.get('video_identificator')) in scraped_videos: # might start causeing problems with huuuge number of videos
		print(vid, "This video has been scraped before")
	else:
		fh.write_to_scraped(str(vid.get('video_identificator')))
		
		try:
			coms = scraper_obj.scrape_comments(vid.get('video_identificator'),vid.get('video_title'),vid.get('channel_name'))
			print("Scraping video with title: %s from channel %s" % (vid.get('video_title'), vid.get('channel_name')))

		except HttpError as err:
			#print(err)

			if err.resp.status in [403,404,500,503]:
				if err.resp.status == 403:
					if HTTP_403_COMMENTS_DISABLED in str(err):
						print("Error 403 - This video has comments disbaled %s " % (vid.get('video_title')))
					if HTTP_403_QUOTA_EXCEEDED in str(err):
						print("You have exceeded your quota")
						isError = True
						break
				if err.resp.status == 404:
					if HTTP_404_NOT_FOUND in str(err) or HTTP_404_CANNOT_BE_FOUND in str(err):
						print("Error 404 - Parameter not found")
				# sys.exit --> jak bedzie ze skonczyla sie quota
			else:
				print("Other error appeared during scraping")
				print(err)
		
if not isError:
	print("INFO: No more videos to scrape, please update scraping_list.txt")


# Get  only username works correctly
# Two methods are needed, you have to make sure that the channel has a legacy name, and the use forUsername
# if the legacy name is not defined then you need to use the channel's id.

#	coms = scraper_obj.scrape_comments(vid.get('video_identificator'),vid.get('video_title') )

#coms =  scraper_obj.scrape_comments(videos[90].get('video_identificator'), videos[90].get('video_title'))
