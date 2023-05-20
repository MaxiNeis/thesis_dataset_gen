import os
from pathlib import Path
import argparse
from configobj import ConfigObj
from utils.videos import *
from utils.subtitles import *
import openai

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
    
    
    
    # Feed ChatGPT
    os.environ['OPENAI_API_KEY'] = "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"
    openai.api_key = os.environ['OPENAI_API_KEY']


    answer_example = """- Diamond push-up: I'm going to go over how to do a diamond
"""

    prepend_messages = [
    {"role": "system", "content": "You are a program that returns bullet points containing relevant data from text."},
    {"role": "user",
        "content": f"Tell me all push-up variations that are explained in detail in the following text as bullet points:\n{full_video_subtitle_block}"},
    {"role": "assistant", "content": answer_example}
    ]
    
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[prepend_messages + {"role": "user", "content": "Tell me all push-up variations that are explained in detail in the following text as bullet points:\n{full_video_subtitle_block}"}])


    print(completion.choices[0].message.content)
    save_chatgpt_answer(completion.choices[0].message.content, query_directory)

if __name__ == "__main__":
    main()