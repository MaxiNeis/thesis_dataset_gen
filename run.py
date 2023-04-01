from pathlib import Path
import argparse
from configobj import ConfigObj
from video_search import searchVideo
from fetch_subtitles import fetch_subtitles

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

    save_as_csv = config['Library'].get('save_as_csv')
    dir = config['Library'].get('dir')
    filename = config['Library'].get('filename')
    file_ext = config['Library'].get('file_ext')
    save_path = Path(dir, ".".join([filename, file_ext]))

    # Search videos
    searchRes_df = searchVideo(query=query, maxRes=maxRes)
    if save_as_csv:
        searchRes_df.to_csv(save_path, index=False)
    
    fetch_subtitles(searchRes_df)
    

if __name__ == "__main__":
    main()