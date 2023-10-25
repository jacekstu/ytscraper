import os
import sys
#print sys.stdout.encoding
from googleapiclient.discovery import build
import json
import requests 
from googleapiclient.errors import HttpError
import datetime

class Scraper:

	def __init__(self, api_key:str, post_url:str):
		
		self.api_key = os.environ.get('API_KEY')
		self.post_url = post_url
		self.youtube = build('youtube', 'v3', developerKey=self.api_key)
		self.video_lt = []
		self.test = []
		self.channel_title = ""

	def save_to_file(self, data:str):
		db_file = open("all_data.txt", "a", encoding="utf-8")
		json.dump(data, db_file, ensure_ascii=False)
	
	def send_to_api(self, obj, endpoint):
		self.http_response = requests.post(self.post_url + endpoint, json=obj)
		#print(self.http_response.content)


	def parse_data_for_json(self, string_data:str) -> str:
		#Turn dictionary into a string for json loading
		self.save_to_file(string_data)
		string_data = str(string_data)
		# Have to replace the single quotes with double quotes
		string_data = string_data.replace("\'", "\"")
		no_links = string_data.replace("<a href=\""," link ")
		no_links2 = no_links.replace("\">","endlink")
		no_brakline = no_links2.replace("<br />"," ")

		return no_brakline

	def pack_json(self, string_data, endpoint):

		data = self.parse_data_for_json(string_data)
		try:
			# READY JSON TO BE SENT TO THE DB
			json_data = json.loads(data)
			#json_final_data = json_data['text'].replace("&quot;","CHUJ CI W CZOKO")
			self.send_to_api(json_data, endpoint)
		except Exception as e:
			pass


	def get_channel_name(self, channel_id):
		
		try:
			self.request = self.youtube.channels().list(
				part=['snippet'],
				id=channel_id
			)
			self.response = self.request.execute()
			return self.response['items'][0]['snippet']['title']

		except HttpError as err:
			if err.resp.status == 403:
				if "cannot be completed because you have exceeded" in str(err):
					print("You have exceeded your API quota")
					sys.exit()

	def get_playlist_id(self, channel):

		try:
			if channel['isLegacy']:
				self.request = self.youtube.channels().list(
				part=['contentDetails'],
				forUsername=channel["channel"]
			)
			else:
				self.request = self.youtube.channels().list(
				part=['contentDetails'],
				id=channel["channel"]
			)

			self.response = self.request.execute()
			return self.response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

		except HttpError as err:

			if err.resp.status in [403,500,503,404]:
				if err.resp.status == 403:
					print("You have exceed your API Calls quota")
			else:
				print("Other error appeard during scraping")
				print(err)

	def add_videos(self, channel_name, published):
		# transform published to date
		published_yy_mm_dd = published.split('-')
		scrape_until = datetime.datetime(int(published_yy_mm_dd[0]), int(published_yy_mm_dd[1]), int(published_yy_mm_dd[2]))

		for vid in self.response['items']:
			published_at = vid['snippet']['publishedAt'].split('T')[0]
			published_at_yy_mm_dd = published_at.split('-')
			do_scrape = datetime.datetime(int(published_at_yy_mm_dd[0]), int(published_at_yy_mm_dd[1]), int(published_at_yy_mm_dd[2]))
			if do_scrape >= scrape_until:
				self.video_lt.append({"video_identificator":vid['snippet']['resourceId']['videoId'], "video_title":vid['snippet']['title'], 'channel_name':channel_name})
			else:
				print("INFO: Video from channel %s is too old for scraping %s" % ( channel_name, vid['snippet']['title']))


	def get_videos(self, playlistId, channel_obj):

			try:
				self.request = self.youtube.playlistItems().list(
					part="snippet", 
					playlistId=playlistId,
					maxResults=50,
				)


				self.response = self.request.execute()

				self.add_videos(channel_obj.get('name'), channel_obj.get('published'))

				isMoreVideos = True if "nextPageToken" in self.response else False

				while isMoreVideos:

					next_page_token = self.response['nextPageToken']

					self.request = self.youtube.playlistItems().list(
						part="snippet", 
						playlistId=playlistId,
						maxResults=50,
						pageToken=next_page_token

					)

					self.response = self.request.execute()

					self.add_videos(channel_obj.get('name'), channel_obj.get('published'))

					isMoreVideos = True if "nextPageToken" in self.response else False


				return self.video_lt

			except HttpError as err:
					pass
					

	def add_comment_to_db(self, video_title):
		# Get video title!

		try:

			for comment in self.response['items']:

				text_displayed = comment["snippet"]["topLevelComment"]["snippet"]["textDisplay"].replace("&#39;", "")
				date = comment["snippet"]["topLevelComment"]["snippet"]["publishedAt"].split('T')[0]
				likes = comment["snippet"]["topLevelComment"]["snippet"]["likeCount"]
				user_id = comment["snippet"]["topLevelComment"]["snippet"]["authorChannelId"]["value"]

				comment_data = {
		
					"channel" : self.channel_title,
					"title" : video_title,
					"text" : text_displayed,
					"imageUrl" : comment["snippet"]["topLevelComment"]["snippet"]["authorProfileImageUrl"],
					"date" : date,
					"author" : comment["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"],
					"link" : "https://www.youtube.com/watch?v=" + comment["snippet"]["topLevelComment"]["snippet"]["videoId"],
					"likes" : likes,
					"userid" : user_id
				}

				user_data = {
					"author" : comment["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"],
					"userid" : user_id
				}
			
				self.pack_json(comment_data, "comments")
				self.pack_json(user_data, "users")
		
		except HttpError as err:
			print(comment)


	def add_reply_to_db(self, reply, video_title):

		date = reply['snippet']['publishedAt'].split('T')[0]


		comment_data = {
			
			"channel" : self.channel_title,
			"title" : video_title,
			"text" : reply['snippet']['textDisplay'].replace("&#39;", ""),
			"imageUrl" : reply['snippet']['authorProfileImageUrl'],
			"date" : date,
			"author" : reply['snippet']['authorDisplayName'],
			"likes" : reply['snippet']['likeCount'],
			"link" : "https://www.youtube.com/watch?v=" + reply['snippet']['videoId'],
			"userid" : reply['snippet']['authorChannelId']['value']
		}

		user_data = {

			"author" : reply['snippet']['authorDisplayName'],
			"userid" : reply['snippet']['authorChannelId']['value']
		}

		self.pack_json(comment_data, "comments")
		self.pack_json(user_data, "users")

	def get_replies(self, video_id, video_title):

		self.request = self.youtube.commentThreads().list(
			part="replies",
			videoId=video_id,
			maxResults=100
		)

		self.response = self.request.execute()
		for comment in self.response['items']:
			if 'replies' in comment:
				for reply in comment['replies']['comments']: 
					self.add_reply_to_db(reply, video_title)
		
		isMoreComments = True if "nextPageToken" in self.response else False

		while isMoreComments:

			self.request = self.youtube.commentThreads().list(
				part="replies",
				videoId=video_id,
				maxResults=100,
				pageToken=self.response['nextPageToken']
			)			

			self.response = self.request.execute()
			for comment in self.response['items']:
				if 'replies' in comment:
					for reply in comment['replies']['comments']: 
						self.add_reply_to_db(reply, video_title)

			isMoreComments = True if "nextPageToken" in self.response else False
		
	def scrape_comments(self, video_id, video_title, channel_name):

		self.channel_title = channel_name

		self.request = self.youtube.commentThreads().list(
			part="snippet",
			videoId=video_id,
			maxResults=100,
			order="time"
		)

		self.response = self.request.execute()

		self.add_comment_to_db(video_title)

		isMoreComments = True if "nextPageToken" in self.response else False


		while isMoreComments:

			self.request = self.youtube.commentThreads().list(
				part="snippet",
				videoId=video_id,
				maxResults=100,
				order="time",
				pageToken=self.response['nextPageToken']
			)			

			self.response = self.request.execute()
			self.add_comment_to_db(video_title)
			isMoreComments = True if "nextPageToken" in self.response else False

		self.get_replies(video_id, video_title)
