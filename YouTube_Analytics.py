
# coding: utf-8

# # Youtube API v3

# In[1]:


import time
import numpy as np
import pandas as pd
from collections import Counter

from YouTube_Scraper import youtube_search


# In[2]:


import seaborn as sns
import matplotlib.pyplot as plt

pltWidth, pltHeight = 20, 10
plt.rcParams['figure.figsize'] = (pltWidth, pltHeight)


# In[3]:


def getYouTubeVideoInfo(query="Hurricane", maxResults=50, order="relevance",
                        token=None, location=None, location_radius=None,
                        publishedAfter=None, publishedBefore=None):

    def mergeDictOfLists(dol1, dol2):
        result = dict(dol1, **dol2)
        result.update((k, dol1[k] + dol2[k]) for k in set(dol1).intersection(dol2))
        return result

    results = None
    nextToken = token
    while True:
        try:
            test, nextToken = youtube_search(query, maxResults, order, nextToken, location,
                                             location_radius, publishedAfter, publishedBefore)
        except KeyError:
            print('Token Error for query:{} with token:{}'.format(query, nextToken))
            nextToken = None
        time.sleep(0.05)
        results = mergeDictOfLists(results, test) if results else test

        if nextToken is None:
            break

    YouTubeVideoDf = pd.DataFrame(data=results)
    YouTubeVideoDf = YouTubeVideoDf[['title', 'viewCount', 'channelTitle', 'commentCount', 'likeCount',
                                     'dislikeCount', 'tags', 'favoriteCount', 'videoId']]
    YouTubeVideoDf.columns = ['Title', 'Views', 'Channel', 'Comment Count', 'Likes', 'Dislikes', 'Tags',
                              'Favourite Count', 'Video ID']
    numericDtypes = ['Views', 'Comment Count', 'Likes', 'Dislikes', 'Favourite Count']
    for i in numericDtypes:
        YouTubeVideoDf[i] = YouTubeVideoDf[i].astype(int)
    YouTubeVideoDf.sort_values(by=['Views'], ascending=False, inplace=True)

    return YouTubeVideoDf


# In[4]:


def getAllDisasterDfs(disasterInfo, startDateFlag=True, endDateFlag=True, order="relevance"):
    """
    Args:
        disasterInfo (list of tuples): Each tuple is of the form (Disaster_Name, Year)
    Returns:
        YouTubeDfsList (list of Dataframes): Each dataframe corresponds to the videos of the
                respective diaster and year from diasterInfo
    """
    disasterDf = {}

    for disasterName, year in disasterInfo:
        query = 'Hurricane ' + disasterName
        publishedAfter = str(year) + '-01-01T00:00:00Z' if startDateFlag else None
        publishedBefore = str(year+2) + '-01-01T00:00:00Z' if endDateFlag else None

        videoDf = getYouTubeVideoInfo(query=query, order=order, publishedAfter=publishedAfter, publishedBefore=publishedBefore)
        disasterDf[disasterName] = videoDf

    return disasterDf


# In[5]:


def removeSpamChannels(videoDfs, channelList=['VEVO'], existsPartly=True):
    for channel in channelList:
        if existsPartly:
            videoDfs = videoDfs[~videoDfs.Channel.str.contains(channel)]
        else:
            videoDfs = videoDfs[~(videoDfs.Channel == channel)]
    return videoDfs


# In[6]:


def plotVideoDf(df1):
    df1 = df1.sort_values(ascending=False, by='Views')
    plt.bar(range(df1.shape[0]), df1['Views'])
    plt.xticks(range(df1.shape[0]), df1['Title'], rotation=90)
    plt.ylabel('Views in 10 millions')
    plt.show()

