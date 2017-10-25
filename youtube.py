import json
import requests
import iso8601
import isodate
import os.path
import random
import config
from urllib.parse import urlparse, parse_qs

def getIdForURL(url):
    url_data = urlparse(url)
    query = parse_qs(url_data.query)
    youtube_id = query['v'][0]
    return youtube_id

def getYoutubeURL(str):
    url = 'https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&key={}&q={}&maxResults=1'.format(config.YT_API_TOKEN,str)
    r = requests.get(url,)
    response = r.json()
    youtube_id = response['items'][0]['id']['videoId']
    video_title = response['items'][0]['snippet']['title']
    youtube_url = 'https://www.youtube.com/watch?v={}'.format(youtube_id)
    return [youtube_url,video_title]

def getTitleForURL(url):
    video_id = getIdForURL(url)
    request_url = 'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={}&key={}'.format(video_id,
                                                                                                  config.YT_API_TOKEN)
    r = requests.get(request_url, )
    response = r.json()
    video_title = response['items'][0]['snippet']['title']
    return video_title

def checkVideoDuration(video_id,limit):
    request_url = 'https://www.googleapis.com/youtube/v3/videos?part=contentDetails&id={}&key={}'.format(video_id,config.YT_API_TOKEN)
    r = requests.get(request_url,)
    response = r.json()
    iso_duration = response['items'][0]['contentDetails']['duration']
    duration = isodate.parse_duration(iso_duration).total_seconds()
    if duration > limit * 60:
        return False
    else:
        return True