import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi


def fetch_subtitles(searchRes_df):
    """
    Save raw subtitles for each video of a query
    """
    for video_ID in searchRes_df['ID']:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_ID)
 
        for transcript in transcript_list:
             print(transcript.fetch())
        #srt = YouTubeTranscriptApi.get_transcript(video_ID)
        #print(srt.text)