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
    full_video_subtitle_block = " ".join(line for line in df_sbttls_raw["text"])
    if bool_save_subtitles:
        save_processed_subtitles(full_video_subtitle_block, subtitles_savepath)
        
    # Ask ChatGPT to identify exercises that are explained in detail
    # Reference / Inspiration: https://arxiv.org/pdf/2304.11633.pdf & https://arxiv.org/pdf/2302.10205.pdf
    CGPT_message_history = []

    CGPT_message_history = dialogue_step(
    persona="""Return all fitness-exercises that are explained in detail in terms of proper execution in a given text. If no fitness-exercises are explained in detail, answer: none. Respond as a list containing the name of the exercise with the form of [Deadlift, Wide-Hands Pushup, Military Press]""",
    #persona="""You are a helpful cooking expert. You answer question by providing a short explanation and a list of easy to follow steps. You list ingredients, tools, and instructions.""",
    msg_history= CGPT_message_history,
    user_query=f"""The given text is: {full_video_subtitle_block}.
    What fitness-exercises in the given text are explained in detail? If no fitness-exercises are explained in detail, answer: none. Respond as a list containing one name per exercise, e.g. [Deadlift, Wide-Hands Pushup, Military Press, Diamond Pushup]"""
    )

    # And why it thinks it is explained deeply
    CGPT_message_history = dialogue_step(
    persona="""Return all fitness-exercises that are explained in detail in terms of proper execution in a given text. Respond as a python dictionary with the following structure: {key: value}, where the key is name name of the exercise and the value is a list of the citations you found""",
    #persona="""You are a helpful cooking expert. You answer question by providing a short explanation and a list of easy to follow steps. You list ingredients, tools, and instructions.""",
    msg_history= CGPT_message_history,
    user_query="""For each fitness-exercise you found earlier, cite the respective passages of the given text that explain only it's proper execution in detail. Group the citations of an exercise as a list, e.g. ["To perform the deadlift you have to adopt a firm stance", "Place your hands about shoulder-wide on the barbell."] and return it alltogether as a python dictionary, meaning the key is the name of the exercise and the value is the respective list."""
    )
    
    # Backtracking the respective citation from chatGPT in the original subtitles to get the video segment starting-time using tf-idf
    # for elem in CGPT_message_history:
    #     print(elem)
    #     print()


if __name__ == "__main__":
    main()