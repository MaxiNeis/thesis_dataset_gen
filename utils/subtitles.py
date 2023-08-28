"""

Utility code used to do all kinds of data-pipelining and -manipulation with the subtitles

"""

import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi
from pathlib import Path


def fetch_subtitles(video_ID: str):
    """
    Get raw subtitles for each video of a result set
    """
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_ID)
    except:
        return False
    df_raw = pd.DataFrame.from_records(transcript_list)
    return df_raw

def save_raw_subtitles(raw_subtitles: pd.DataFrame, video_ID: str, video_title: str, subtitles_path: Path):
    """
    Save raw subtitles
    """
    filename = f"{video_title}_{video_ID}_raw.csv"
    raw_subtitles.to_csv(Path(subtitles_path,filename), index=False)
    print(f'Raw subtitles saved in: {Path(subtitles_path,filename)}')
    
def save_processed_subtitles(processed_subtitles: str, video_ID: str, video_title: str, subtitles_path: Path):
    """
    Save processed subtitles
    """
    filename = f"{video_title}_{video_ID}_processed.csv"
    with open(Path(subtitles_path, filename), "w") as file:
        file.write(processed_subtitles)
    print(f'Processed subtitles saved in: {Path(subtitles_path,filename)}')

def save_chatgpt_answer(processed_subtitles: str, subtitles_path: Path):
    """
    Save processed subtitles
    """
    with open(Path(subtitles_path,"processed.txt"), "w") as file:
        file.write(processed_subtitles)
    print(f'Processed subtitles saved in: {Path(subtitles_path,"processed.txt")}')



