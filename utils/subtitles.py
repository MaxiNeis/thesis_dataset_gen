"""

Utility code used to do all kinds of data-pipelining and -manipulation with the subtitles

"""

import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi
from pathlib import Path
import os
from slugify import slugify
from difflib import SequenceMatcher


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
    builtup_sentences = []
    testword_occurances = []

    for i, csentence in enumerate(corpus):
        # Get all occurences of the first word of the sentene in the currently inspected subtitle part.
        # For each starting point, everything left of it will be cut. To the right it will be filled up with words to the desired target_length.
        # Finally for each sentence built by this way the similarity to the sentence from ChatGPT will be calculated.
        words_csen_original = csentence.lower().split(" ")
        starting_points = [i for i, word in enumerate(words_csen_original) if word == words_sen[0]]
        if starting_points:
            testword_occurances.append(len(starting_points))
        for starting_point in starting_points:
            # Fill csentence with words of next csentence(s) up to the length of len(sentence) + word_offset
            j = i + 1
            target_length = len(words_sen) + word_offset
            # Re-initiate words_csen with original words to allow to use cutoff w/ the next starting point that was calculated with the original lengths
            words_csen = words_csen_original 
            words_csen = words_csen[starting_point:] 
            while len(words_csen) < target_length and j < len(corpus):
                extra_words = corpus[j].split(" ")
                words_needed = target_length - len(words_csen)
                if words_needed >= len(extra_words):
                    extra_words = " ".join(extra_words)
                elif words_needed < len(extra_words):
                    extra_words = " ".join(extra_words[:words_needed])
                csentence = " ".join(words_csen) + " " + extra_words if extra_words else " ".join(words_csen)
                words_csen = csentence.split(" ")
                j += 1
            builtup_sentences.append(csentence)
            # If first word in csentence
    # For each sentence in builtup_sentences calculate similarity to sentence from ChatGPT.
    # Do this by taking buffer words into account -> from builtup_sentences+len(buffer_words) (as they are in the list) to builtup_sentences-len(buffer_words)
    # The highest similarity will be the best match
    for sentence in builtup_sentences:
        for i in range(2*word_offset):
            sentence.rsplit(' ', 1)[0]

        


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

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


