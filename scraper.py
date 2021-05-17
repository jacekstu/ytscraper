import os
import sys
#print sys.stdout.encoding
from googleapiclient.discovery import build
import json
import requests 
from googleapiclient.errors import HttpError

class Scraper:

	def __init__(self, api_key, post_url):
		
		self.api_key = os.environ.get('API_KEY')
		self.post_url = post_url
		self.youtube = build('youtube', 'v3', developerKey=self.api_key)
		self.video_lt = []
		self.test = []
		self.channel_title = ""

	def save_to_file(self, data):
		db_file = open("all_data.txt", "a", encoding="utf-8")
		json.dump(data, db_file, ensure_ascii=False)
	
	def send_to_api(self, obj):
		self.http_response = requests.post(self.post_url, json=obj)


	def parse_data_for_json(self, string_data):
		#Turn dictionary into a string for json loading
		self.save_to_file(string_data)
		string_data = str(string_data)
		# Have to replace the single quotes with double quotes
		string_data = string_data.replace("\'", "\"")
		no_links = string_data.replace("<a href=\""," link ")
		no_links2 = no_links.replace("\">","endlink")
		no_brakline = no_links2.replace("<br />"," ")

		return no_brakline

	def pack_json(self, string_data):

		data = self.parse_data_for_json(string_data)
		try:
			# READY JSON TO BE SENT TO THE DB
			json_data = json.loads(data)
			#json_final_data = json_data['text'].replace("&quot;","CHUJ CI W CZOKO")
			self.send_to_api(json_data)
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

	def add_videos(self, channel):
		for vid in self.response['items']:
			self.video_lt.append({"video_identificator":vid['snippet']['resourceId']['videoId'], "video_title":vid['snippet']['title'], 'channel_name':channel})

	def get_videos(self, playlistId, channel):

			try:
				self.request = self.youtube.playlistItems().list(
					part="snippet", 
					playlistId=playlistId,
					maxResults=50,
				)


				self.response = self.request.execute()

				self.add_videos(channel)

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

					self.add_videos(channel)

					isMoreVideos = True if "nextPageToken" in self.response else False

				return self.video_lt

			except HttpError as err:
					pass
					

	def add_comment_to_db(self, video_title):
		# Get video title!

		for comment in self.response['items']:

			text_displayed = comment["snippet"]["topLevelComment"]["snippet"]["textDisplay"].replace("&#39;", "")
			date = comment["snippet"]["topLevelComment"]["snippet"]["publishedAt"].split('T')[0]
			likes = comment["snippet"]["topLevelComment"]["snippet"]["likeCount"]

			comment_data = {
		
				"channel" : self.channel_title,
				"title" : video_title,
				"text" : text_displayed,
				"imageUrl" : comment["snippet"]["topLevelComment"]["snippet"]["authorProfileImageUrl"],
				"date" : date,
				"author" : comment["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"],
				"link" : "https://www.youtube.com/watch?v=" + comment["snippet"]["topLevelComment"]["snippet"]["videoId"],
				"likes" : likes
			}
			
			self.pack_json(comment_data)

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
			"link" : "https://www.youtube.com/watch?v=" + reply['snippet']['videoId']
		}

		self.pack_json(comment_data)

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
