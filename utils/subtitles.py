"""

Utility code used to do all kinds of data-pipelining and -manipulation with the subtitles

"""

import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi
from pathlib import Path
import os
from slugify import slugify


def fetch_subtitles(video_ID: str):
    """
    Get raw subtitles for each video of a result set
    """
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_ID)
    except:
        return None
    df_raw = pd.DataFrame.from_records(transcript_list)
    return df_raw

def save_raw_subtitles(raw_subtitles: pd.DataFrame, video_ID: str, video_title: str, subtitles_path: Path):
    """
    Save raw subtitles
    """
    clean_video_title = slugify(os.path.splitext(video_title)[0])
    filename = f"{clean_video_title}_{video_ID}_raw.csv"
    raw_subtitles.to_csv(Path(subtitles_path,filename), index=False)
    print(f'Raw subtitles saved in: {Path(subtitles_path,filename)}')
    
def save_processed_subtitles(processed_subtitles: str, video_ID: str, video_title: str, subtitles_path: Path):
    """
    Save processed subtitles
    """
    clean_video_title = slugify(os.path.splitext(video_title)[0])
    filename = f"{clean_video_title}_{video_ID}_processed.csv"
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

def get_timestamp(sentence: str, raw_subtitles: pd.DataFrame, word_offset: int = 5) -> (int, int):
    """
    Return tuple of start and end timestamp of a sentence
    """
    corpus = raw_subtitles['text'].tolist()
    words_sen = sentence.split(" ")
    for i, csentence in enumerate(corpus):
        # Get all occurences of the first word of the sentene in the currently inspected subtitle part.
        # For each starting point, everything left of it will be cut. To the right it will be filled up with words to the desired target_length.
        # Finally for each sentence built by this way the similarity to the sentence from ChatGPT will be calculated.
        words_csen_original = csentence.split(" ")
        starting_points = [i for i, word in enumerate(words_csen) if word == words_sen[0]]
        builtup_sentences = []
        for starting_point in starting_points:

            # Fill csentence with words of next csentence(s) up to the length of csentence + word_offset
            j = i + 1
            words_csen = words_csen_original
            target_length = len(words_sen) + word_offset
            while len(words_csen) < target_length and j < len(corpus):
                extra_words = corpus[j].split(" ")
                words_needed = target_length - len(words_csen)
                if words_needed >= len(extra_words):
                    extra_words = " ".join(extra_words)
                elif words_needed < len(extra_words):
                    extra_words = " ".join(extra_words[:words_needed])
                csentence = csentence + " " + extra_words if extra_words else csentence
                words_csen = csentence.split(" ")
                j += 1
            builtup_sentences.append(csentence)
            # If first word in csentence
            if words_sen[0] in csentence:
                # Compare offset from first word to last word in sentece and corpus. If its the same and the sentence is the same (with very small degree of freedom for mistakes from ChatGPT), return timestamp. 
                words_csentence = csentence.split(" ")


            # if len(sentence) <= len(csentence):
            #     # Make sure to also have last word of sentence in csentence as a rough check
            #     if words_sen[-1] in words_csentence:
            #         print(f"Found sentence: {sentence}")
            #         print(f"Found csentence: {csentence}")
            #         #return raw_subtitles['start'][i], raw_subtitles['duration'][i]
            # # Here we need to join sentence from one or more corpus sentences
            # elif len(sentence) > len(csentence) + word_offset:
            #     overhang = len(sentence) - len(csentence) + word_offset
            #     while overhang > 0:
            #         i += 1
            #         csentence += corpus[i]
            #         overhang = len(sentence) - len(csentence)

def find_highest_similarity(sentence: str, corpus_sentence: str, word_offset: int = 5):
    """
    IN: - Sentence from ChatGPT.
        - Corpus sentence suggestion. It is determined by:
            1. Finding the sarting word of the sentence in the corpus
            2. Adding len(sentence) + word_offset to the starting word found.
    Returns: The substring of the corpus sentence suggestion that has the highest similarity to the sentence from ChatGPT.
             Substring is determined by removing 2*word_offset from the end word by word
    """ 
    pass



