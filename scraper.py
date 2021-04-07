import os
import sys
#print sys.stdout.encoding
from googleapiclient.discovery import build

class Scraper:

	def __init__(self, api_key):
		
		self.api_key = os.environ.get('API_KEY')
		self.youtube = build('youtube', 'v3', developerKey=self.api_key)

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
			self.video_lt.append(vid['snippet']['resourceId']['videoId'])

	def get_videos(self, playlistId):

		self.video_lt = []

		self.request = self.youtube.playlistItems().list(
			part="snippet", 
			playlistId=playlistId,
			maxResults=50
		)

		self.response = self.request.execute()

		#for vid in self.response['items']:
		#	self.video_lt.append(vid['snippet']['resourceId']['videoId'])
		self.add_videos()

		isMoreVideos = True if "nextPageToken" in self.response else False

		while isMoreVideos:
			next_page_token = self.response['nextPageToken']
			print(next_page_token)
			self.request = self.youtube.playlistItems().list(
				part="snippet", 
				playlistId=playlistId,
				maxResults=50,
				pageToken=next_page_token

			)
			self.response = self.request.execute()
		#	for vid in self.response['items']:
		#		self.video_lt.append(vid['snippet']['resourceId']['videoId'])
			self.add_videos()

			isMoreVideos = True if "nextPageToken" in self.response else False

		return self.video_lt
