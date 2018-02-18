#!/usr/bin/env/python3.6

import os
import time
from twitter import *
import urllib.request
import praw
import os
import random

import creds # auth info

# @author David Worley, david@davidworley.com
# @date 11/28/2016
# Created for my personal bot @worleyBot on Twitter


def authenticate(): # easier on the eyes
	return Twitter(auth=OAuth(creds.token, creds.token_secret, creds.consumer_key, creds.consumer_secret))


# This function grabs a random picture from /r/dankmemes and tweets it.
def tweetRedditMeme():
	r = praw.Reddit(client_id=creds.client_id, client_secret=creds.client_secret,
                     password=creds.password, user_agent=creds.user_agent,
                     username=creds.username)
	meme = r.subreddit('dankmemes+offensivememes').random()
	urllib.request.urlretrieve(meme.url, "dank.jpg")
	with open("dank.jpg", "rb") as imagefile:
		img = imagefile.read()
	t = authenticate() # authenticates my Twitter account credentials
	t_upload = Twitter(domain='upload.twitter.com',
		auth=OAuth(creds.token, creds.token_secret, creds.consumer_key, creds.consumer_secret))
	imgID = t_upload.media.upload(media=img)["media_id_string"]
	t.statuses.update(media_ids=imgID)
	os.remove("dank.jpg") # delete temporarily-created file

# ------------------------------------------------- #

def tweetTopMeme():
    r = praw.Reddit(client_id=creds.client_id, client_secret=creds.client_secret,
                     password=creds.password, user_agent=creds.user_agent,
                     username=creds.username)
    while True:
        try:
            choice = random.randint(0, 1999)
            counter = 0
            for item in r.subreddit('memes+dankmemes+funny').top('all', limit=2000):
                if (counter == choice):
                    meme = item
                    print(counter)
                    break
                counter = counter + 1
                # print(counter)
            urllib.request.urlretrieve(meme.url, "dank.jpg")
            with open("dank.jpg", "rb") as imagefile:
        	    img = imagefile.read()
            t = authenticate() # authenticates my Twitter account credentials
            t_upload = Twitter(domain='upload.twitter.com',
                auth=OAuth(creds.token, creds.token_secret, creds.consumer_key, creds.consumer_secret))
            imgID = t_upload.media.upload(media=img)["media_id_string"]
            t.statuses.update(media_ids=imgID)
            os.remove("dank.jpg") # delete temporarily-created file
        except:
            continue
        else:
            break


# Using Tumblr API to find random short text posts to convert to a tweet
def tweetRandomTumblrPost():
	# http://best-of-text-posts.tumblr.com/random
	# Grab text in between: \n\u201c and \n\u201d for now (trial)
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
				# print('grabbed: ' + formattedText)
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
		t.statuses.update(status=tweetToPost)
		time.sleep(60*30)


# ------------------------------------------------- #

tweetTopMeme()
