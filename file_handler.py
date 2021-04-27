
class Handler:

	def __init__(self, filename):
		self.filename = filename
		self.done_videos = []


	def get_scraped_videos(self):
		with open(self.filename,'r', encoding="utf-8") as f:
			for vid in f:
				self.done_videos.append(vid.strip())
		return self.done_videos

	def write_to_scraped(self, video):
		with open(self.filename, 'a+', encoding="utf-8") as f:
			f.write(video + "\n")