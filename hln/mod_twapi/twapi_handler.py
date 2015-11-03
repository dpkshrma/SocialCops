"""Module to handle twitter api stream data"""
import math
import json
import copy
import tweepy
from datetime import datetime
from datetime import timedelta
import hln.mod_twapi.doc_templates as dt
import hln.mod_twapi.config as twapi_config

class Scraper():
	"""Fetches tweets from twitter streaming api using tweepy module"""

	tweets_limit = 3000
	count_per_page = 200
	page_limit = 6
	page = 0

	leads = []

	reporters = []
	reporter_ids = set()

	no_exception = True

	def __init__(self, init_scrape=True):
		"""oauth tweepy using twitter app credentials
		
		Args:
		    init_scrape (bool, optional): run scrape function if true
		"""
		auth = tweepy.OAuthHandler(twapi_config.consumer_key, twapi_config.consumer_secret)
		auth.set_access_token(twapi_config.access_token, twapi_config.access_token_secret)
		self.twapi = tweepy.API(auth)
		if init_scrape:
			self.scrape()

	def scrape(self):
		"""Fetch tweet objects get relevant data as docs
		
		Returns None
		"""
		tl=self.tweets_limit
		cpp=self.count_per_page

		self.page_limit = int(math.ceil(tl/float(cpp)))

		print("Fetching twitter api stream pages...")

		while self.no_exception:
			self.page += 1
			print("on page - "+str(self.page))
			tweets = None

			if self.page <= self.page_limit:
				try:
					# get tweets from home_timeline of user
					tweets = self.twapi.home_timeline(page=self.page, count=cpp)
				except tweepy.TweepError as inst:
					# print("Tweepy Exception : ")
					# print(inst)
					self.no_exception = False
					break
			else:
				break

			if (tweets is None) or (len(tweets) == 0):
				break

			for tweet in tweets or []:
				# get tweet in json format
				tweet = tweet._json

				# extract lead information from tweet
				lead_doc = self.get_lead_doc(tweet)

				# store lead
				self.leads.append(lead_doc)

				# check if reporter exists
				if lead_doc["reporter_id"] and lead_doc["reporter_id"] not in self.reporter_ids:
					# store visited reporter id
					self.reporter_ids.add(lead_doc["reporter_id"])

					# create new reporter entry
					reporter_doc = self.get_reporter_doc(tweet)

					# store reporter
					self.reporters.append(reporter_doc)

	def get_lead_doc(self, tweet):
		"""Extracts relevant information from tweet for ES lead doc
		
		Args:
		    tweet (dict): tweet
		
		Returns:
		    dict: ES lead doc
		"""
		# copy doc from template
		lead_doc = copy.deepcopy(dt.lead_doc)

		# lead metadata
		lead_doc["id"] = tweet.get("id") or 0
		# get date in format used in es mapping
		created_at = tweet.get("created_at")
		if created_at:
			utc_offset = int((tweet.get("user") or {}).get("utc_offset") or 0)
			created_at = convert_to_utc_time(created_at, utc_offset)
		lead_doc["created_at"] = created_at
		lead_doc["reporter_id"] = ((tweet.get("user") or {}).get("id"))

		# lead location
		coord = tweet.get("coordinates")

		if coord and len(coord) == 2:
			lead_doc["location"] = coord

		# lead data
		lead_doc["data"]["text"] = tweet.get("text")

		if "entities" in tweet:
			entities = tweet.get("entities")
			lead_doc["categories"] = [entity['text'] for entity in (entities.get("hashtags") or {})]
			for entity in (entities.get("media") or {}):
				lead_doc["data"]["media"].append({
					"id": entity["id"],
					"media_url": entity["media_url"],
					"type": entity["type"]
				})
			for entity in (entities.get("user_mentions") or {}):
				lead_doc["data"]["entities"].append({
					"id": entity["id"],
					"name": entity["name"],
					"screen_name": entity["screen_name"]
				})

		return lead_doc

	def get_reporter_doc(self, tweet):
		"""Extracts relevant information from tweet for ES reporter doc
		
		Args:
		    tweet (dict): tweet
		
		Returns:
		    dict: ES reporter doc
		"""
		user = tweet.get("user") or {}
		reporter_doc = copy.deepcopy(dt.reporter_doc)

		# handle nested attributes here.

		# store user values in reporter_doc
		for k in reporter_doc:
			reporter_doc[k] = user.get(k)
			if k == 'created_at':
				utc_offset = int((tweet.get("user") or {}).get("utc_offset") or 0)
				reporter_doc[k] = convert_to_utc_time(reporter_doc[k], utc_offset)

		return reporter_doc

def convert_to_utc_time(dt_obj, utc_offset):
	"""Converts given time to utc time
	
	Args:
	    dt_obj (datetime.datetime object): input time
	    utc_offset (int): utc offset from input time in seconds
	
	Returns:
	    datetime.datetime: utc datetime
	"""
	dt_obj = datetime.strptime(str(dt_obj),'%a %b %d %H:%M:%S +0000 %Y')
	off_sign = 1
	if utc_offset:
		off_sign = utc_offset/abs(utc_offset)
	utc_time = dt_obj - timedelta(seconds=abs(utc_offset))*off_sign
	dt_obj = utc_time
	dt_obj = dt_obj.strftime("%Y/%m/%d %I:%M:%S")
	return dt_obj