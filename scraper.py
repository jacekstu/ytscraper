import os
import sys
#print sys.stdout.encoding
from googleapiclient.discovery import build
import json


class Scraper:

	def __init__(self, api_key):
		
		self.api_key = os.environ.get('API_KEY')
		self.youtube = build('youtube', 'v3', developerKey=self.api_key)
		self.video_lt = []
		self.test = []

	def save_to_file(self, data):
		db_file = open("all_data.txt", "a", encoding="utf-8")
		json.dump(data, db_file, ensure_ascii=False)
	

	def parse_data_for_json(self, string_data):
		#Turn dictionary into a string for json loading
		self.save_to_file(string_data)
		string_data = str(string_data)
		# Have to replace the single quotes with double quotes
		string_data = string_data.replace("\'", "\"")
		no_links = string_data.replace("<a href=\"","link")
		no_links2 = no_links.replace("\">","endlink")
		return no_links2

	def pack_json(self, string_data):

		data = self.parse_data_for_json(string_data)

		try:
			# READY JSON TO BE SENT TO THE DB
			json_data = json.loads(data)
		except Exception as e:
			pass


	def get_playlist_id(self, channel):

		if channel["isLegacy"]:
			self.request = self.youtube.channels().list(
				part=['contentDetails'],
				forUsername=channel["channel"]
			)
		else:
			self.request = self.youtube.channels().list(
				part=['contentDetails'],
				id=channel["channel"]
			)

		try:
			self.response = self.request.execute()
			return self.response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

		except Exception as e:
			print(e)
			return 0

	def add_videos(self):
		for vid in self.response['items']:
			self.video_lt.append({"video_identificator":vid['snippet']['resourceId']['videoId'], "video_title":vid['snippet']['title']})

	def get_videos(self, playlistId):

		self.request = self.youtube.playlistItems().list(
			part="snippet", 
			playlistId=playlistId,
			maxResults=50,
		)

		self.response = self.request.execute()

		self.add_videos()

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

			self.add_videos()

			isMoreVideos = True if "nextPageToken" in self.response else False

		return self.video_lt

	def add_comment_to_db(self, video_title):
		# Get video title!
		for comment in self.response['items']:
		

			text_displayed = comment["snippet"]["topLevelComment"]["snippet"]["textDisplay"].replace("&#39;", "")

			comment_data = {
		
				"title" : video_title,
				"text" : text_displayed,
				"image_url" : comment["snippet"]["topLevelComment"]["snippet"]["authorProfileImageUrl"],
				"publication_date" : comment["snippet"]["topLevelComment"]["snippet"]["publishedAt"],
				"author" : comment["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"],
				"link" : "https://www.youtube.com/watch?v=" + comment["snippet"]["topLevelComment"]["snippet"]["videoId"]
			}
			
			self.pack_json(comment_data)

	def add_reply_to_db(self, reply, video_title):
		
		comment_data = {
			
			"title" : video_title,
			"text" : reply['snippet']['textDisplay'].replace("&#39;", ""),
			"image_url" : reply['snippet']['authorProfileImageUrl'],
			"publication_date" : reply['snippet']['publishedAt'],
			"author" : reply['snippet']['authorDisplayName'],
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
		
	def scrape_comments(self, video_id, video_title):

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




