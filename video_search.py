import googleapiclient.discovery
import pandas as pd
import jmespath
from tabulate import tabulate

api_service_name = "youtube"
api_version = "v3"
api_key = "AIzaSyD5Ui6dgMEdc_GskasNSnIxUHGezzbhuoc" # <YOUTUBE_API_KEY> insert your key here

youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey = api_key)

videolink_prefix = 'https://www.youtube.com/watch?v='

metadata_template = {
'Title': "snippet.title",
'ID': "id.videoId",
'Link' :  "id.videoId",               
'Description': "snippet.description",
'Published At': "snippet.publishedAt", 
'Channel Title': "snippet.channelTitle",
'Channel ID': "snippet.channelId",
'QueryTerm': None,
'Caption': None,
}

def searchVideo(query:str = None, relatedVid:str = None, maxRes:int = 1, channelId:str = None, caption:str = 'any', lang:str = 'en'):
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
        for field, jamespath in metadata_template.items():
            if jamespath:
                videoData[field] = jmespath.search(jamespath, video)
        # Data processing
        videoData['Link'] = 'https://www.youtube.com/watch?v=' + videoData['Link']
        videoData['Query Term'] = query
        videoData['Caption'] = caption
        videoList.append(videoData)
    video_df = pd.DataFrame(videoList)
    return video_df

