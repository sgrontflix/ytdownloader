import sys
import os
import subprocess
import re
import argparse
from pytube import YouTube


def youtube_url_validation(url):
    """
    Checks whether the URL passed is a valid YouTube URL or not

    :param url: URL to be validated
    :return: true if the URL given is a valid YouTube URL, false if it is not
    """
    youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)' \
                    r'\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'

    youtube_regex_match = re.match(youtube_regex, url)

    return youtube_regex_match


def sanitize_string(string):
    """
    Replaces all forbidden characters with ''

    :param string: string to be sanitized
    :return: sanitized string
    """
    chars = '\\/:*?"<>|'
    for c in chars:
        string = string.replace(c, '')

    return string


def remove_files(files):
    """
    Removes all files inside the list passed as argument

    :param files: list containing files to remove
    :return: None
    """
    for file in files:
        try:
            os.remove(file)
        except OSError:
            print_error(f'Couldn\'t delete {file}. Aborting script...')
            sys.exit(1)


# initialize parser and set arguments
parser = argparse.ArgumentParser()
parser.add_argument('ffmpeg_path', help='Path to FFmpeg executable')
parser.add_argument('url', help='URL of the video you want to download')
parser.add_argument('-a', '--audio', action='store_true', help='Only download the audio')
parser.add_argument('-g', '--gpu', action='store_true', help='Use GPU to merge audio and video tracks (recommended if '
                                                             'you have an NVIDIA GPU)')
parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')

# get arguments
args = parser.parse_args()

ffmpeg_path = args.ffmpeg_path
yt_url = args.url
audio_only = args.audio
gpu = args.gpu
verbose = args.verbose


# these functions will print the passed string if verbose=true or do nothing otherwise
def print_status(string): print('[*] ' + string) if verbose else lambda *a, **k: None


def print_error(string): print('[-] ' + string) if verbose else lambda *a, **k: None


def print_good(string): print('[+] ' + string) if verbose else lambda *a, **k: None


disable_verbose = ' -hide_banner -loglevel panic'
enable_gpu = ' -hwaccel cuda -hwaccel_output_format cuda'
merge_command = ffmpeg_path + (enable_gpu if gpu else '') + (disable_verbose if not verbose else '') + ' -i video.mp4' \
                                                                                                       ' -i audio.mp4' \
                                                                                                       ' -c:v copy' \
                                                                                                       ' -c:a copy'

if not youtube_url_validation(yt_url):
    print_error("Please, provide a valid YouTube URL.")
    sys.exit(1)

# get yt link info
yt = YouTube(yt_url)

audio_track = yt.streams.filter(only_audio=True, file_extension='mp4').order_by('bitrate')[-1]

if audio_only:
    print_status('Downloading audio track...')
    audio_track.download()
else:
    video_track = yt.streams.filter(progressive=False, file_extension='mp4').order_by('resolution')[-1]
    # remove all forbidden characters from the title so the script doesn't crash
    title = sanitize_string(video_track.title)

    print_status('Downloading video.mp4...')
    video_track.download(filename='video')
    print_good('video.mp4 successfully downloaded.')

    print_status('Downloading audio.mp4...')
    audio_track.download(filename='audio')
    print_good('audio.mp4 successfully downloaded.')

    print_status('Merging tracks...')
    try:
        output = subprocess.check_output(f'{merge_command} \"{title}.mp4\"')
        print_good(f'Tracks successfully merged into \"{title}.mp4\".')
    except subprocess.CalledProcessError:
        print_error(f'Couldn\'t merge tracks. Error code: {subprocess.CalledProcessError.returncode}.')

    # delete redundant video and audio tracks
    print_status('Deleting redundant audio and video tracks...')
    remove_files(['video.mp4', 'audio.mp4'])
    print_good('Tracks successfully deleted.')

print_status("Finished processing file. Exiting script...")
