import os
from pathlib import Path
import argparse
from configobj import ConfigObj
from utils.videos import *
from utils.subtitles import *
from utils.chatGPT import *

def main():
    """
    Main Function
    """
    # Initializion
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config-file', default='./config.ini', help='specify config file', metavar='FILE')
    args = parser.parse_args()

    config = ConfigObj(args.config_file)

    query = config['Query'].get('query')
    maxRes = config['Query'].get('maxResults')
    openAI_API_KEY = config['API'].get('chatGPT')

    bool_save_resultset = config['Library'].get('save_resultset_as_csv')
    bool_save_subtitles = config['Library'].get('save_subtitles')
    data_dir = config['Library'].get('data_dir')
    title = config['Library'].get('title')
    file_ext = config['Library'].get('file_ext')

    # One directory per config.ini where everything is saved
    query_directory = Path(data_dir, title)
    videos_savepath = Path(query_directory, ".".join([title, file_ext]))
    subtitles_savepath = Path(query_directory,"subtitles")

    # Make sure directory is there if needed
    if bool_save_resultset or bool_save_subtitles:
        if not os.path.exists(query_directory):
            os.makedirs(query_directory)
        if bool_save_subtitles:
            if not os.path.exists(subtitles_savepath):
                os.makedirs(subtitles_savepath)
    
    # Get video resultset
    df_searchRes = searchVideos(query=query, maxRes=maxRes)
    if bool_save_resultset:
        df_searchRes.to_csv(videos_savepath, index=False)
        print(f'Resultset saved in: {videos_savepath}')
    
    # Get each video's raw subtitles from API
    df_sbttls_raw = fetch_subtitles(df_searchRes)
    if bool_save_subtitles:
        save_raw_subtitles(df_sbttls_raw, subtitles_savepath)

    # Process subtitles to get the full text
    full_video_subtitle_block = " ".join(line for line in df_sbttls_raw["text"])
    if bool_save_subtitles:
        save_processed_subtitles(full_video_subtitle_block, subtitles_savepath)
    
    print(full_video_subtitle_block)
    
    talk_with(
    persona="""You are a helpful cooking expert. You answer question by providing a short explanation and a list of easy to follow steps. You list ingredients, tools, and instructions.""",
    tell_user=print,
    ask_user=input
    )
    
    talk_with(full_video_subtitle_block, openAI_API_KEY)

if __name__ == "__main__":
    main()