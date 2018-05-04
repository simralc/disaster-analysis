from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import pandas as pd
import pprint
import matplotlib.pyplot as pd

DEVELOPER_KEY = "AIzaSyBtP0FXmxqJWESMoNDw8rZ4EKCSPt2HuTQ"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
__UNKNOWN_STR__ = '__UNKNOWN__'
__UNKNOWN_INT__ = 0

def youtube_search(q, max_results=50, order="relevance", token=None, location=None, location_radius=None, publishedAfter=None, publishedBefore=None):

	youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

	search_response = youtube.search().list(
						q=q,
						type="video",
						pageToken=token,
						order=order,
						part="id,snippet", # Part signifies the different types of data you want
						maxResults=max_results,
						location=location,
						locationRadius=location_radius,
						publishedAfter=publishedAfter,
						publishedBefore=publishedBefore).execute()

	title, videoId = [], []
	channelId, channelTitle, categoryId, tags = [], [], [], []
	favoriteCount, viewCount, likeCount, dislikeCount = [], [], [], []
	category, commentCount, videos = [], [], []

	for search_result in search_response.get("items", []):
		'''
			search_result['id']['kind'] in ['youtube#video', 'youtube#channel', 'youtube#playlist']
			The ids are respectively one of search_result['id']['videoId'], search_result['id']['channelId'], search_result['id']['playlistId']
		'''
		if search_result["id"]["kind"] == "youtube#video":

			response = youtube.videos().list(
				part='statistics, snippet',
				id=search_result['id']['videoId']).execute()

			# if ('items' not in response) or ('snippet' not in response['items'][0]) or ('statistics' not in response['items'][0]):
			# 	break
			try:
				snippet = response['items'][0]['snippet']
				statistics = response['items'][0]['statistics']
				title.append(search_result['snippet']['title'])
				videoId.append(search_result['id']['videoId'])

				# channelId += [snippet['channelId']] if 'channelId' in snippet else [__UNKNOWN_STR__]
				channelTitle += [snippet['channelTitle']] if 'channelTitle' in snippet else [__UNKNOWN_STR__]
				# categoryId += [snippet['categoryId']] if 'categoryId' in snippet else [__UNKNOWN_STR__]
				favoriteCount += [statistics['favoriteCount']] if 'favoriteCount' in statistics else [__UNKNOWN_INT__]
				viewCount += [statistics['viewCount']] if 'viewCount' in statistics else [__UNKNOWN_INT__]
				likeCount += [statistics['likeCount']] if 'likeCount' in statistics else [__UNKNOWN_INT__]
				dislikeCount += [statistics['dislikeCount']] if 'dislikeCount' in statistics else [__UNKNOWN_INT__]

				commentCount += [statistics['commentCount']] if 'commentCount' in statistics else [__UNKNOWN_INT__]
				tags += [snippet['tags']] if 'tags' in snippet else [[__UNKNOWN_STR__]]

			except IndexError:
				print(token, q, publishedAfter, publishedBefore)
				print(response['items'])

	youtube_dict = {
	'tags': tags,
	# 'channelId': channelId,
	'channelTitle': channelTitle,
	# 'categoryId': categoryId,
	'title': title,
	'videoId': videoId,
	'viewCount': viewCount,
	'likeCount': likeCount,
	'dislikeCount': dislikeCount,
	'commentCount': commentCount,
	'favoriteCount': favoriteCount,
	}

	nextPageToken = search_response['nextPageToken'] if 'nextPageToken' in search_response else None
	return youtube_dict, nextPageToken