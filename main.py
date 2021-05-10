from utilities import *
from pathlib import Path
from pytube import YouTube
import sys
import subprocess
import argparse


if __name__ == '__main__':
    # initialize parser and set arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('ffmpeg_path', help='Path to FFmpeg executable')
    parser.add_argument('url', help='URL of the video you want to download')
    parser.add_argument('-a', '--audio', action='store_true', help='Only download the audio')
    parser.add_argument('-g', '--gpu', action='store_true', help='Use GPU to merge audio and video tracks '
                                                                 '(recommended if you have an NVIDIA GPU)')
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
    merge_command = '\"' + ffmpeg_path + '\" -y' + (enable_gpu if gpu else '') + \
                    (disable_verbose if not verbose else '') + ' -i video.mp4 -i audio.mp4 -c:v copy -c:a copy'

    if not youtube_url_validation(yt_url):
        print_error('Invalid URL detected, aborting script...')
        sys.exit(1)

    ffmpeg_executable = Path(ffmpeg_path)
    if not ffmpeg_executable.is_file():
        print_error('Invalid path detected, aborting script...')
        sys.exit(1)

    # get yt link info
    yt = YouTube(yt_url)

    audio_track = yt.streams.filter(only_audio=True, file_extension='mp4').order_by('bitrate')[-1]

    if audio_only:
        print_status('Downloading audio track...')
        audio_path = audio_track.download()
        if audio_track.exists_at_path(audio_path):
            print_good('Audio track successfully downloaded.')
        else:
            print_error('Couldn\'t download audio track.')
    else:
        video_track = yt.streams.filter(progressive=False, file_extension='mp4').order_by('resolution')[-1]
        # remove all forbidden characters from the title so the script doesn't crash
        title = sanitize_string(video_track.title)

        print_status('Downloading video.mp4...')
        video_path = video_track.download(filename='video')
        if video_track.exists_at_path(video_path):
            print_good('video.mp4 successfully downloaded.')
        else:
            print_error('Couldn\'t download video.mp4.')
            sys.exit(1)

        print_status('Downloading audio.mp4...')
        audio_path = audio_track.download(filename='audio')
        if audio_track.exists_at_path(audio_path):
            print_good('audio.mp4 successfully downloaded.')
        else:
            print_error('Couldn\'t download audio.mp4.')
            sys.exit(1)

        print_status('Merging tracks...')
        try:
            output = subprocess.check_output(f'{merge_command} \"{title}.mp4\"', shell=True)
            print_good(f'Tracks successfully merged into \"{title}.mp4\".')
        except subprocess.CalledProcessError:
            print_error(f'Couldn\'t merge tracks. Error code: {subprocess.CalledProcessError.returncode}.')

        # delete redundant video and audio tracks
        print_status('Deleting redundant audio and video tracks...')
        result = remove_files(['video.mp4', 'audio.mp4'])
        if result:
            print_good('Tracks successfully deleted.')
        else:
            print_error(f'Couldn\'t delete one or more tracks.')
