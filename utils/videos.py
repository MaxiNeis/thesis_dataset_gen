"""

Utility code used to retrieve a result set of YouTube videos via YouTube's API given a query term.

The result set - stored as DataFrame - does not contain the actual videos but the most important metadata about them.
Which metadata is stored is defined by param 'videoData_template'.

"""

import googleapiclient.discovery
import pandas as pd
import jmespath
from pytube import YouTube
from datetime import timedelta

api_service_name = "youtube"
api_version = "v3"
api_key = "AIzaSyD5Ui6dgMEdc_GskasNSnIxUHGezzbhuoc" # <YOUTUBE_API_KEY> insert your key here

youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey = api_key)

videolink_prefix = 'https://www.youtube.com/watch?v='

videoData_template = {
'Title': 'snippet.title',
'ID': 'id.videoId',
'Link' :  'id.videoId',
'Description': 'snippet.description',
'Published At': 'snippet.publishedAt', 
'Channel Title': 'snippet.channelTitle',
'Channel ID': 'snippet.channelId',
'QueryTerm': None,
'Caption': None,
}

def searchVideos(query:str = None, relatedVid:str = None, maxRes:int = 1, channelId:str = None, caption:str = 'any', lang:str = 'en'):
    """
    Search for videos with the Youtube API
    If relatedVid is specified then query and channel cannot be defined
    IN:
        query: Search query. The default is None.
        relatedVid: Optional. The default is None.
        maxRes: Optional, maximum number of results. The default is 1.
        channelId: Specifiy which channel by ID. The default is None. 
        caption: 'any', 'closedCaption' (only videos with captions, auto-captions not included) or 'none'. The default is 'any'. 
        lang: 'de', 'en' -> Language of the videos. The default is 'en'
    Return:
        video_df: Pandas DataFrame of metadata of the generated videos. 
            Metadata columns are: title, videoId, videoLink, description, publishedAt,
            channelTitle, channelId, queryTerm, caption.
    """
    request = youtube.search().list(
    part = "id,snippet",
    type = "video",
    q = query,
    relatedToVideoId = relatedVid,
    relevanceLanguage = lang,
    channelId = channelId,
    videoCaption = caption,
    maxResults = maxRes,
    )

    response = request.execute()
    videoList = []

    # Save metadata of a video in a library
    for video in response['items']:
        videoData = {}
        for field, jamespath in videoData_template.items():
            if jamespath:
                videoData[field] = jmespath.search(jamespath, video)
        # Data processing
        videoData['Link'] = 'https://www.youtube.com/watch?v=' + videoData['Link']
        videoData['Query Term'] = query
        videoData['Caption'] = caption
        videoList.append(videoData)
    video_df = pd.DataFrame(videoList)
    return video_df


def download_videos(video_dir_savepath: str, video_ID: str, video_title: str):
    yt = YouTube(f"https://www.youtube.com/watch?v={video_ID}").streams.filter(res="720p").first().download(video_dir_savepath)

def get_length(video_url: str):
    yt = YouTube(video_url)
    return timedelta(seconds=yt.length)
