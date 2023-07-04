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

    query = config['Query'].get('query')
    maxRes = config['Query'].get('maxResults')
    openai.api_key = config['API'].get('chatGPT')

    bool_save_resultset = config['Library'].get('save_resultset_as_csv')
    bool_save_subtitles = config['Library'].get('save_subtitles')
    data_dir = config['Library'].get('data_dir')
    title = config['Library'].get('title')
    file_ext = config['Library'].get('file_ext')

    # One directory per config.ini / its query where everything is saved
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
        # Save link separately as .txt for easier manual access
        link = df_searchRes['Link']
        with open(Path(query_directory, 'link.txt'), 'w') as f:
            f.write(link.to_string(index=False))
        print(f'Resultset saved in: {videos_savepath}')
    
    # Get each video's raw subtitles from API
    df_sbttls_raw = fetch_subtitles(df_searchRes)
    if bool_save_subtitles:
        save_raw_subtitles(df_sbttls_raw, subtitles_savepath)

    # Process subtitles to get the full text block (subtitles are returned per video segment together with start-time and duration)
    subtitles = " ".join(line for line in df_sbttls_raw["text"])
    if bool_save_subtitles:
        save_processed_subtitles(subtitles, subtitles_savepath)
    print(df_searchRes['Link'])
        
    # Ask ChatGPT to identify exercises that are explained in detail
    # Reference / Inspiration: https://arxiv.org/pdf/2304.11633.pdf & https://arxiv.org/pdf/2302.10205.pdf
    gpt = personas['ThreeStep-Trainer-Persona'](subtitles)
    
    # Backtracking the respective citation from chatGPT in the original subtitles to get the video segment starting-time using tf-idf
    # for elem in CGPT_message_history:
    #     print(elem)
    #     print()


if __name__ == "__main__":
    main()