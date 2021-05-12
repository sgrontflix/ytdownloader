from utilities import *
from pathlib import Path
from pytube import YouTube
import sys
import argparse


if __name__ == '__main__':
    # initialize parser and set arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('ffmpeg_path', help='Path to FFmpeg executable')
    parser.add_argument('url', help='URL of the video you want to download')
    parser.add_argument('-r', '--resolution', default='2160p', help='Preferred resolution '
                                                                    'of the video you want to download')
    parser.add_argument('-a', '--audio', action='store_true', help='Only download the audio')
    parser.add_argument('-g', '--gpu', action='store_true', help='Use GPU to merge audio and video tracks '
                                                                 '(recommended if you have an NVIDIA GPU)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')

    # get arguments
    args = parser.parse_args()

    ffmpeg_path = args.ffmpeg_path
    yt_url = args.url
    resolution = args.resolution
    audio_only = args.audio
    gpu = args.gpu
    verbose = args.verbose

    # these functions will print the passed string if verbose=true or do nothing otherwise
    def print_status(string): print('[*] ' + string) if verbose else lambda *a, **k: None


    def print_error(string): print('[-] ' + string) if verbose else lambda *a, **k: None


    def print_good(string): print('[+] ' + string) if verbose else lambda *a, **k: None


    if not youtube_url_validation(yt_url):
        print_error('Invalid URL detected, aborting script...')
        sys.exit(1)

    if not Path(ffmpeg_path).is_file():
        print_error('Invalid path detected, aborting script...')
        sys.exit(1)

    # get yt link info
    yt = YouTube(yt_url)

    audio_track = yt.streams.filter(only_audio=True, file_extension='mp4').order_by('bitrate')[-1]

    # remove all forbidden characters from the title so the script doesn't crash
    title = sanitize_string(audio_track.title)

    if audio_only:
        print_status('Downloading audio track...')
        audio_path = audio_track.download(filename=title)
        if audio_track.exists_at_path(audio_path):
            print_good(f'{title}.mp4 successfully downloaded.')
        else:
            print_error('Couldn\'t download audio track.')

            if Path(audio_path).is_file():
                print_status('Cleaning up...')
                result = remove_files([f'{title}.mp4'])
                # a list is False if empty, True if not
                if not result:
                    print_good(f'{title}.mp4 deleted.')
                else:
                    print_error(f'Couldn\'t delete {title}.mp4.')
    else:
        if gpu and not is_gpu_available():
            print_error('Couldn\'t find any NVIDIA GPU installed.')
            print_status('Tracks will be merged using the CPU.')
            gpu = False

        disable_verbose = ' -hide_banner -loglevel panic'
        enable_gpu = ' -hwaccel cuda -hwaccel_output_format cuda'
        merge_command = '\"' + ffmpeg_path + '\" -y' + (enable_gpu if gpu else '') + \
                        (disable_verbose if not verbose else '') + ' -i video.mp4 -i audio.mp4 -c:v copy -c:a copy'

        resolution_list = ['2160p', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p']

        if resolution not in resolution_list:
            print_error('Invalid resolution detected, aborting script...')
            sys.exit(1)

        video_track = \
            yt.streams.filter(progressive=False, file_extension='mp4', resolution=resolution).order_by('fps')

        # if at least a video track with the given resolution was found, select the best one (highest fps)
        if video_track:
            video_track = video_track[-1]
        # otherwise select the video track with the highest possible resolution and fps
        else:
            print_error('Missing video track for the given resolution.')
            print_status('Selecting the highest possible resolution video track.')
            video_track = \
                yt.streams.filter(progressive=False, file_extension='mp4').order_by('resolution').order_by('fps')[-1]

        print_status('Downloading video.mp4...')
        video_path = video_track.download(filename='video')
        if video_track.exists_at_path(video_path):
            print_good('video.mp4 successfully downloaded.')
        else:
            print_error('Couldn\'t download video.mp4.')

            if Path(video_path).is_file():
                print_status('Cleaning up...')
                result = remove_files(['video.mp4'])
                if not result:
                    print_good('video.mp4 deleted.')
                else:
                    print_error('Couldn\'t delete video.mp4.')

            sys.exit(1)

        print_status('Downloading audio.mp4...')
        audio_path = audio_track.download(filename='audio')
        if audio_track.exists_at_path(audio_path):
            print_good('audio.mp4 successfully downloaded.')
        else:
            print_error('Couldn\'t download audio.mp4.')

            print_status('Cleaning up...')
            result = remove_files(['video.mp4'])
            if not result:
                print_good('video.mp4 deleted.')
            else:
                print_error('Couldn\'t delete video.mp4.')

            if Path(audio_path).is_file():
                result = remove_files(['audio.mp4'])
                if not result:
                    print_good('audio.mp4 deleted.')
                else:
                    print_error('Couldn\'t delete audio.mp4.')

            sys.exit(1)

        print_status('Merging tracks...')
        try:
            pipeline(f'{merge_command} \"{title}.mp4\"')
            print_good(f'Tracks successfully merged into \"{title}.mp4\".')
        except Exception:
            print_error('Couldn\'t merge tracks.')

        # delete redundant video and audio tracks
        print_status('Deleting redundant audio and video tracks...')
        result = remove_files(['video.mp4', 'audio.mp4'])
        if not result:
            print_good('Tracks successfully deleted.')
        else:
            print_error('Couldn\'t delete the following track(s): ' + ', '.join([str(track) for track in result]) + '.')
