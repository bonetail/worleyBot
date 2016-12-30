#!/usr/bin/env/python3.5

import config
import os
import time
from twitter import *
import random
import string
import urllib.request
import urllib.error
import requests
import multiprocessing
from multiprocessing import Process
import re
# from imgurpython import ImgurClient

# @author David Worley, david@davidworley.com
# @date 11/28/2016
# Created for my personal bot @worleyBot on Twitter

#token = auth.token
#token_secret = auth.token_secret
#consumer_key = auth.consumer_key
#consumer_secret = auth.consumer_secret

def authenticate():
	# read secure info to login to Twitter
	t = Twitter(auth=OAuth(config.token, config.token_secret, config.consumer_key, config.consumer_secret))
	return t

# Function to scrape random picture from imgur subreddit galleries or regular galleries
# Currently tries random URL combinations in the /r/dankmemes subreddit gallery until it doesn't 404.
# Implement multiprocessing for this method in main method to speed search up.
def tweetRandomMeme():
	while True:
		t = authenticate()
		combo = ''
		foundImage = False
		while foundImage == False:
			combo = ''.join(random.sample(string.ascii_letters+string.digits, 7))
			print("Proc #" + str(p.pid) + ": https://imgur.com/r/dankmemes/" + combo)
			img = requests.get("https://imgur.com/r/dankmemes/" + combo)
			# print(img.status_code)
			if (img.status_code < 400):
				foundImage = True
		print("--- FOUND IMAGE ---")
		url = "https://i.imgur.com/" + rndm + ".jpg"
	
		urllib.request.urlretrieve(url, "temp.jpg")
		
		with open("temp.jpg", "rb") as imagefile:
			imagedata = imagefile.read()
	
		t_upload = Twitter(domain='upload.twitter.com',
	    	auth=OAuth(config.token, config.token_secret, config.consumer_key, config.consumer_secret))	
		imgID = t_upload.media.upload(media=imagedata)["media_id_string"]
		t.statuses.update(status="Hourly update: I found this somewhere on the internet to show you guys!", media_ids=imgID)

		os.remove('temp.jpg')

# Used 'DownThemAll!' Firefox addon to download entire /r/dankmemes subreddit collection
# Tweets a random picture from the directory, removes it, and caches picture name in txt file
def tweetDankMeme():
	t = authenticate()
	while True:
		chosenPic = random.choice(os.listdir('dank-db/'))
#		print(chosenPic)
		chosenPic = 'dank-db/' + chosenPic
		with open(chosenPic, "rb") as imagefile:
 			imagedata = imagefile.read()
		t_upload = Twitter(domain='upload.twitter.com',
		auth=OAuth(config.token, config.token_secret, config.consumer_key, config.consumer_secret))
		imgID = t_upload.media.upload(media=imagedata)["media_id_string"]
		t.statuses.update(media_ids=imgID)
		
		with open('used-dank.txt', 'a') as myfile:
			myfile.write(str(chosenPic) + '\n')
		os.remove(chosenPic)
#		print("MEME: DONE. Waiting...")
		time.sleep(60*60)

# Using Tumblr API to find random short text posts to convert to a tweet
def tweetRandomTumblrPost():
	# http://best-of-text-posts.tumblr.com/random
	# Grab text in between: \n\u201c and \n\u201d
	t = authenticate()
	while True:
		foundText = False
		tweetToPost = ''
		while foundText == False: # until it finds a short enough post to tweet
			url = urllib.request.urlopen('http://best-of-text-posts.tumblr.com/random').read().decode('utf-8')
			post = re.findall(r"\\n\\u201c (.*?)\\n\\u201d", url)
			postLength = len(post)
			if postLength == 0:
				print('failed to find any text. trying again...')
				continue
			for i in range(postLength):
				formattedText = post[i].encode('utf-8').decode('unicode_escape').encode('ascii','ignore').decode('ascii','ignore')
#				print('grabbed: ' + formattedText)
				if len(formattedText) < 129:
					foundText = True
					doneRemovingUsernames = False
					while not doneRemovingUsernames:
						if ':\n ' in formattedText:
							head, sep, tail = formattedText.partition(':\n ')
							formattedText = tail
						else:
							doneRemovingUsernames = True;
					tweetToPost = formattedText
					tweetToPost = tweetToPost + '\n#worleybot'
					break
#		print('trying to post: ' + tweetToPost)
		t.statuses.update(status=tweetToPost)
#		print('TUMBLR: DONE. Waiting...')
		time.sleep(60*30)
	
# --- MAIN --- #

# # Loop that creates multiprocesses for tweetRandomMeme to find a valid submission URL
# for i in range(30):
#	p = Process(target=tweetRandomMeme, name=str(i))
#	print("Process #" + str(i) + " has started")
#	p.start()

# tweetDankMeme(): sleeps 60 minutes upon success before returning
# tweetRandomTumblrPost(): sleeps 30 minutes upon success before returning
memeProcess = Process(target=tweetDankMeme)
memeProcess.start()
tumblrPost = Process(target=tweetRandomTumblrPost)
tumblrPost.start()
