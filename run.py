import os
from pathlib import Path
import argparse
from configobj import ConfigObj
from utils.videos import *
from utils.subtitles import *
from utils.general import *
from personas.chatGPT import *
from personas import personas
import nltk
import concurrent.futures


def main():
    """
    Main Function
    """
    # Initializion
    parser = argparse.ArgumentParser()
    userDir = os.path.expanduser('~')
    parser.add_argument('-c', '--config-file', default=str(Path(userDir,'Dropbox\Thesis\Repo','config.ini')), help='specify config file', metavar='FILE')
    parser.add_argument('-v', '--video', default='', help='specify a video ID that you want to examine')
    args = parser.parse_args()

    config = ConfigObj(args.config_file)

    query = config['Query']['query']
    maxRes = int(config['Query']['maxResults'])
    balancing = config['Query']['balancing']

    openai.api_key = config['chatGPT']['API']

    save_resultset = config['Library'].as_bool('save_resultset_as_csv')
    save_subtitles = config['Library'].as_bool('save_subtitles')
    data_dir = config['Library']['data_dir']
    title = config['Library']['title']
    file_ext = config['Library']['file_ext']
    runFromCSV = config['Library'].as_bool('run_from_csv')

    save_videos = config['Video'].as_bool('save_videos')

    query_assessment = config['Query_Assessment'].as_bool('run_assessment')
    save_assessment_results = config['Query_Assessment'].as_bool('save_assessment_results')
    q_ass_sample_size = config['Query_Assessment']['sample_size']


    # One directory per config.ini / its query where everything is saved
    query_directory = Path(data_dir, title)
    videos_libr_savepath = Path(query_directory, ".".join([title, file_ext]))
    chatGPT_results_directory = Path(query_directory,"chatGPT_results")
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
    if not runFromCSV:
        df_searchRes = createVideoDF(query=query, maxRes=maxRes, balancing=balancing)
    else:
        df_searchRes = pd.read_csv(videos_libr_savepath)
    
    if save_resultset and not runFromCSV:
        df_searchRes.to_csv(videos_libr_savepath,  index=False)
        # Save link separately as .txt for easier manual access
        link = df_searchRes['Link']
        with open(Path(query_directory, 'links.txt'), 'w') as f:
            f.write(link.to_string(index=False))
        print(f'Resultset saved in: {videos_libr_savepath}')
    
    print(df_searchRes)
    
    if args.video:
        df_searchRes = df_searchRes[df_searchRes['ID'] == args.video]
        print(f'Only examining video with ID {args.video}')
        print(df_searchRes)

    if query_assessment:
        # Initialize Monte Carlo Sim result table
        mc_analysis = pd.DataFrame(columns=['ID','Title','Length','MC runs','# None','# Wrong Format','# Invalid Citations','Rate "Exercise Found" [%]', 'Rate "Python Dict Returned" [%]', 'Rate "Citation Correct" [%]'])
    elif not query_assessment:
        mc_analysis = ''

    # Main routine
    for video_ID, video_title, video_length in zip(df_searchRes['ID'], df_searchRes['Title'], df_searchRes['Length']):
        
        # For convenience while programming
        print('https://www.youtube.com/watch?v=' + video_ID)

        # Remove special characters from video title for saving purposes
        video_title = slugify(os.path.splitext(video_title)[0])

        # Get each video's raw subtitles from API
        df_sbttls_raw = fetch_subtitles(video_ID)
        print(df_sbttls_raw)
        if save_subtitles:
            save_raw_subtitles(df_sbttls_raw, video_ID, video_title, subtitles_savepath)

        # Download each video if desired
        if save_videos == True:
            download_videos(videos_dir_savepath, video_ID, video_title)
        
        # Add video to MC table if desired
        if query_assessment:
            if video_ID not in mc_analysis['ID']:
                mc_analysis.loc[len(mc_analysis)] = {'ID':video_ID,'Title':video_title,'Length':video_length,'MC runs':0,'# None':0,'# Wrong Format':0, '# Invalid Citations': 0,'Rate "Exercise Found" [%]':0,'Rate "Python Dict Returned" [%]':0, 'Rate "Citation Correct" [%]': 0}

        # Process subtitles to get text-only (subtitles are returned per video segment / together with start-time and duration)
        subtitles = " ".join(line for line in df_sbttls_raw["text"])
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        print(len(nltk.word_tokenize(subtitles)))
        if len(nltk.word_tokenize(subtitles)) > 3550:
            print("Warning: Subtitles are longer than 3550 tokens. This might cause problems with the GPT-3 API as additional tokens are needed for the query and 4097 tokens is the limit. Cutting off at 3550 tokens.")
            subtitles = " ".join(elem for elem in nltk.word_tokenize(subtitles)[:3550])
        if save_subtitles:
            save_processed_subtitles(subtitles, video_ID, video_title, subtitles_savepath)

        runs = 1
        if query_assessment:
            runs = int(q_ass_sample_size)
            
        gpt = None
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futurelist = {executor.submit(askGPT, subtitles, query_assessment, mc_analysis, video_ID): i for i in range(runs)}
            for future in concurrent.futures.as_completed(futurelist):
                cnt = futurelist[future]
                try:
                    gpt = future.result()
                except Exception as e:
                    print(f"Try no. {cnt} with video {video_ID} failed.")
                    print(e)

        #print(mc_analysis)
        # Calculate rates
        if query_assessment:
            mc_analysis.loc[mc_analysis.ID==video_ID,['Rate "Exercise Found" [%]']] = 100 - (int(mc_analysis.loc[mc_analysis.ID==video_ID,['# None']].values[0][0]) / int(mc_analysis.loc[mc_analysis.ID==video_ID,['MC runs']].values[0][0])) * 100
            mc_analysis.loc[mc_analysis.ID==video_ID,['Rate "Python Dict Returned" [%]']] = 100 - (int(mc_analysis.loc[mc_analysis.ID==video_ID,['# Wrong Format']].values[0][0]) / int(mc_analysis.loc[mc_analysis.ID==video_ID,['MC runs']].values[0][0])) * 100
            mc_analysis.loc[mc_analysis.ID==video_ID,['Rate "Citation Correct" [%]']] = 100 - (int(mc_analysis.loc[mc_analysis.ID==video_ID,['# Invalid Citations']].values[0][0]) / int(mc_analysis.loc[mc_analysis.ID==video_ID,['MC runs']].values[0][0])) * 100
            print(mc_analysis)
        
        # Backtracking the respective citation from chatGPT in the original subtitles to get the video segment starting-time using tf-idf
        # Take the last gpt object returned if query_assessment is turned on
        for exercise in gpt.getResult():
            for explanations in gpt.getResult()[exercise]:
                print(explanations)

    if query_assessment and save_assessment_results:
        mc_analysis.to_csv(Path(query_directory, 'query_assessment.csv'), index=False)

    if not runFromCSV:
        gpt.saveResult(video_ID, chatGPT_results_directory)

        

def askGPT(subtitles, query_assessment, mc_analysis, video_ID):
    # Ask ChatGPT to identify exercises that are explained in detail
    # Reference / Inspiration: https://arxiv.org/pdf/2304.11633.pdf & https://arxiv.org/pdf/2302.10205.pdf
    gpt = personas['ThreeStep-Trainer-Persona'](subtitles)
    
    if query_assessment:
        mc_analysis.loc[mc_analysis.ID==video_ID,['MC runs']] = mc_analysis.loc[mc_analysis.ID==video_ID,['MC runs']] + 1
        # Check that result != None
        if gpt.getResult() == 'None':
            mc_analysis.loc[mc_analysis.ID==video_ID,['# None']] = mc_analysis.loc[mc_analysis.ID==video_ID,['# None']] + 1
        if not gpt.getResult():
            mc_analysis.loc[mc_analysis.ID==video_ID,['# None']] = mc_analysis.loc[mc_analysis.ID==video_ID,['# None']] + 1
        else:
            try:
                # Another case of result != None
                if 'None' in gpt.getResult().keys():
                    mc_analysis.loc[mc_analysis.ID==video_ID,['# None']] = mc_analysis.loc[mc_analysis.ID==video_ID,['# None']] + 1
                # Invalid citations / no exercise found / the same 'exercise description' citations returned for every exercise
                else:
                    if not is_valid_citation(gpt.getResult()):
                        mc_analysis.loc[mc_analysis.ID==video_ID, ['# Invalid Citations']] = mc_analysis.loc[mc_analysis.ID==video_ID, ['# Invalid Citations']] + 1
            # Wrong format / no dict returned
            except AttributeError:
                mc_analysis.loc[mc_analysis.ID==video_ID,['# Wrong Format']] = mc_analysis.loc[mc_analysis.ID==video_ID,['# Wrong Format']] + 1
    return gpt

if __name__ == "__main__":
    main()