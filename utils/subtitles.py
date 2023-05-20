"""

Utility code used to do all kinds of data-pipelining and -manipulation with the subtitles

"""

import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi
from pathlib import Path


def fetch_subtitles(df_videos: pd.DataFrame):
    """
    Get raw subtitles for each video of a result set
    """
    for video_ID in df_videos['ID']:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_ID)
        df_raw = pd.DataFrame.from_records(transcript_list)
    return df_raw

def save_raw_subtitles(raw_subtitles: pd.DataFrame, subtitles_path: Path):
    """
    Save raw subtitles
    """
    raw_subtitles.to_csv(Path(subtitles_path,"raw.csv"), index=False)
    print(f'Raw subtitles saved in: {Path(subtitles_path,"raw.csv")}')
    
def save_processed_subtitles(processed_subtitles: str, subtitles_path: Path):
    """
    Save processed subtitles
    """
    with open(Path(subtitles_path,"processed.txt"), "w") as file:
        file.write(processed_subtitles)
    print(f'Processed subtitles saved in: {Path(subtitles_path,"processed.txt")}')

def save_chatgpt_answer(processed_subtitles: str, subtitles_path: Path):
    """
    Save processed subtitles
    """
    with open(Path(subtitles_path,"processed.txt"), "w") as file:
        file.write(processed_subtitles)
    print(f'Processed subtitles saved in: {Path(subtitles_path,"processed.txt")}')



