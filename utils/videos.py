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
from utils.subtitles import *
import concurrent.futures

api_service_name = "youtube"
api_version = "v3"
api_key = "AIzaSyD5Ui6dgMEdc_GskasNSnIxUHGezzbhuoc" # <YOUTUBE_API_KEY> insert your key here

youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey = api_key)

videolink_prefix = 'https://www.youtube.com/watch?v='

videoData_template = {
'Title': 'snippet.title',
'ID': 'id.videoId',
'Length': None,
'Link' :  None,
'isShort': None,
'Description': 'snippet.description',
'Published At': 'snippet.publishedAt',
'Channel Title': 'snippet.channelTitle',
'Channel ID': 'snippet.channelId',
'QueryTerm': None,
'Caption': None,
}

def searchVideos(query:str = None, relatedVid:str = None, maxRes:int = 1, channelId:str = None, caption:str = 'none', lang:str = 'en'):
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
    Note:
        Caption parameter is a serious API functionality limitation for this project.
        This is because you cannot
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
        videoData['Length'] = get_length(videolink_prefix + videoData['ID'])
        videoData['Link'] = videolink_prefix + videoData['ID']
        # Unfortunately, getting the information of wether a video is a short or not is not a trivial task and too much for this project.
        # Therefore as a workaround we simply decide by taking the video length into account whether a video is a short or not, building on the premise that the effect for the thesis stays the same (compressed visual information).
        videoData['isShort'] = True if videoData['Length'] < timedelta(minutes=1) else False
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

def createVideoDF(query:str = None, relatedVid:str = None, maxRes:int = 1, channelId:str = None, caption:str = 'any', lang:str = 'en', balancing:str = None, maxResOriginal:int = None, run = 1):
    """
    Get more videos than originally requested to account for videos without subtitles or with wrong format
    """
    if run == 1:
        maxResOriginal = maxRes
    run +=1
    results = searchVideos(query = query, relatedVid = relatedVid, maxRes = maxRes, channelId = channelId, caption = caption, lang = lang)
    # process resultset, i.e. remove videos that don't fit (= without subtitles and/or wrong format)
    badResults = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futurelist = {executor.submit(fetch_subtitles, videoID): videoID for videoID in results['ID']}
        for future in concurrent.futures.as_completed(futurelist):
            videoID = futurelist[future]
            if future.result() is None:
                badResults.append(videoID)
    moreBadResults = check_for_wrong_format(results, balancing)
    if moreBadResults:
        remove = list(set(badResults) | set(moreBadResults))
    else: remove = badResults
    results = results[~results['ID'].isin(remove)]

    if len(results) < maxResOriginal:
        maxRes += len(remove)
        results = createVideoDF(query = query,
                                relatedVid = relatedVid, 
                                maxRes = maxRes, 
                                channelId = channelId, 
                                caption = caption, 
                                lang = lang, 
                                balancing = balancing, 
                                maxResOriginal = maxResOriginal, 
                                run = run)
    return results.head(maxResOriginal)

def check_for_wrong_format(results: pd.DataFrame, balancing: str = None):
    """
    Returns: a list of unfitting videos by videoID (to meet the requested balancing) or None if the balanacing requirement is met
    """
    if not balancing or balancing == 'none':
        return None
    elif balancing == 'balanced':
        pass
    elif balancing == 'shorts_only':
        if False in results['isShort'].values:
            return list(results['ID'][results['isShort'] == False])
        else:
            return None
    elif balancing == 'normal_only':
        if True in results['isShort']:
            return list(results['ID'][results['isShort'] == True])
        else:
            return None
    else:
        raise ValueError(f'Balancing {balancing} not implemented. Please specify a described balancing method from config.ini')
