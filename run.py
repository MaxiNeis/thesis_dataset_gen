import os
from pathlib import Path
import argparse
from configobj import ConfigObj
from utils.videos import *
from utils.subtitles import *
from personas.chatGPT import *
from personas import personas

def main():
    """
    Main Function
    """
    # Initializion
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config-file', default='./config.ini', help='specify config file', metavar='FILE')
    args = parser.parse_args()

    config = ConfigObj(args.config_file)

    query = config['Query']['query']
    maxRes = config['Query']['maxResults']

    openai.api_key = config['chatGPT']['API']

    save_resultset = config['Library'].as_bool('save_resultset_as_csv')
    save_subtitles = config['Library'].as_bool('save_subtitles')
    data_dir = config['Library']['data_dir']
    title = config['Library']['title']
    file_ext = config['Library']['file_ext']

    save_videos = config['Video'].as_bool('save_videos')

    query_assessment = config['Query_Assessment'].as_bool('run_assessment')
    q_ass_sample_size = config['Query_Assessment']['sample_size']



    # One directory per config.ini / its query where everything is saved
    query_directory = Path(data_dir, title)
    videos_libr_savepath = Path(query_directory, ".".join([title, file_ext]))
    subtitles_savepath = Path(query_directory,"subtitles")
    videos_dir_savepath = Path(query_directory,"videos")

    # Make sure directories are there if needed
    if save_resultset or save_subtitles or save_videos:
        if not os.path.exists(query_directory):
            os.makedirs(query_directory)
        if save_subtitles:
            if not os.path.exists(subtitles_savepath):
                os.makedirs(subtitles_savepath)
        if save_videos:
            if not os.path.exists(videos_dir_savepath):
                os.makedirs(videos_dir_savepath)
    
    # Get video resultset
    df_searchRes = searchVideos(query=query, maxRes=maxRes)
    if save_resultset:
        df_searchRes.to_csv(videos_libr_savepath, index=False)
        # Save link separately as .txt for easier manual access
        link = df_searchRes['Link']
        with open(Path(query_directory, 'links.txt'), 'w') as f:
            f.write(link.to_string(index=False))
        print(f'Resultset saved in: {videos_libr_savepath}')
        print(df_searchRes)



    # Main routine
    for video_ID, video_title in zip(df_searchRes['ID'], df_searchRes['Title']):

        # Get each video's raw subtitles from API
        df_sbttls_raw = fetch_subtitles(video_ID)
        if save_subtitles:
            save_raw_subtitles(df_sbttls_raw, video_ID, video_title, subtitles_savepath)

        # Download each video if desired
        if save_videos == True:
            download_videos(videos_dir_savepath, video_ID, video_title)

        # Process subtitles to get text-only (subtitles are returned per video segment / together with start-time and duration)
        subtitles = " ".join(line for line in df_sbttls_raw["text"])
        if save_subtitles:
            save_processed_subtitles(subtitles, video_ID, video_title, subtitles_savepath)
        
        # For convenience while programming
        print('https://www.youtube.com/watch?v=' + video_ID)

        runs = 1
        if query_assessment:
            runs = int(q_ass_sample_size)
            
        # Ask ChatGPT to identify exercises that are explained in detail
        # Reference / Inspiration: https://arxiv.org/pdf/2304.11633.pdf & https://arxiv.org/pdf/2302.10205.pdf
        for x in range(runs):
            gpt = personas['ThreeStep-Trainer-Persona'](subtitles)
        
        # Backtracking the respective citation from chatGPT in the original subtitles to get the video segment starting-time using tf-idf
        print("Return Ergebnis: " + gpt.getResult())

        # Monte Carlo Sim:
        # Checking two distinct cases:
        #   1. How often does None appear?
        #   2. How often does gpt.getResult() return invalid format?


if __name__ == "__main__":
    main()