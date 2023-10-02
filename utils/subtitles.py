"""

Utility code used to do all kinds of data-pipelining and -manipulation with the subtitles

"""

import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi
from pathlib import Path
import os
from slugify import slugify
from difflib import SequenceMatcher
from operator import itemgetter


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
    builtup_sentences = {}
    bs_count = 0
    testword_occurances = []

    for i, csentence in enumerate(corpus):
        # Get all occurences of the first word of the sentene in the currently inspected subtitle part.
        # For each starting point, everything left of it will be cut. To the right it will be filled up with words to the desired target_length.
        # Finally for each sentence built by this way the similarity to the sentence from ChatGPT will be calculated.
        words_csen_original = csentence.lower().split(" ")
        starting_points = [i for i, word in enumerate(words_csen_original) if word == words_sen[0]]
        if starting_points:
            for i in starting_points:
                starting_points_derived_timestamps = 100 - (len(words_csen_original)-i) * 100
        for starting_point in starting_points:
            # Fill csentence with words of next csentence(s) up to the length of len(sentence) + word_offset
            j = i + 1
            target_length = len(words_sen) + word_offset
            # Re-initiate words_csen with original words to allow to use cutoff w/ the next starting point that was calculated with the original lengths
            words_csen = words_csen_original
            # Cut off left of the starting word
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
                j2 = j
                if j2 == len(corpus): # last iteration, next one will be skipped as j < len(corpus) will be false
                    j2 -= 1 # Decrease by one to be able to use it as index for raw_subtitles
            # Add each sentence (all its variants that were builtup) to dict as well as their starting point calculated from j which denotes how many next sentences were used
            builtup_sentences[bs_count] = (csentence, raw_subtitles['start'][i], raw_subtitles['start'][j2]) # (Starting timestamp, Ending timestamp)
            bs_count += 1
            # If first word in csentence
    # For each sentence in builtup_sentences calculate similarity to sentence from ChatGPT.
    # Do this by taking buffer words into account -> from builtup_sentences+len(buffer_words) (as they are in the list) to builtup_sentences-len(buffer_words)
    # The highest similarity will be the best match
    similarities = []
    for key in builtup_sentences.keys():
        # Cutting off word by word until len(sentence) - word_offset. For the first sentence no cutoff is done (j == 0)
        for j in range(2*word_offset):
            similarities.append((similar(builtup_sentences[key][0].rsplit(' ', j)[0], sentence), key, j))
    best_score, key, j = max(similarities, key = itemgetter(0))
    best_sent_raw, best_start, best_end = builtup_sentences[key]
    best_sent = best_sent_raw.rsplit(' ', j)[0]
    print(best_sent)
    print(sentence)

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


