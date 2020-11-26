import sys
import os
import re
import argparse
from pytube import YouTube
from moviepy import editor as mpe


def youtube_url_validation(url):
    """
    Check whether the url passed is a valid YouTube URL or not

    :param url: URL to be validated
    :return: true if the URL given is a valid YouTube URL, false if it is not
    """
    youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)' \
                    r'\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'

    youtube_regex_match = re.match(youtube_regex, url)
    if youtube_regex_match:
        return youtube_regex_match

    return youtube_regex_match


def combine_tracks(video_file, audio_file, out_file, fps=25):
    """
    Combine video and audio track into one file

    :param video_file: path to video track
    :param audio_file: path to audio track
    :param out_file: path to merged file
    :param fps: fps of the video
    :return: None
    """
    video = mpe.VideoFileClip(video_file)
    audio = mpe.AudioFileClip(audio_file)
    out = video.set_audio(audio)
    out.write_videofile(out_file, fps=fps)

    # close readers to avoid PermissionError: [WinError 32] when deleting temporary files
    video.close()
    audio.close()
    out.close()


# initialize parser and set arguments
parser = argparse.ArgumentParser()
parser.add_argument("url", help="URL of the video you want to download")
parser.add_argument("-a", action="store_true", help="Only download the audio")

# get arguments
args = parser.parse_args()

yt_url = args.url
audio_only = args.a

if not youtube_url_validation(yt_url):
    print("Please, provide a valid YouTube URL.")
    sys.exit()

# get yt link info
yt = YouTube(yt_url)

audio_track = yt.streams.filter(only_audio=True, file_extension='mp4').order_by('bitrate')[-1]

if audio_only:
    audio_track.download()
else:
    video_track = yt.streams.filter(progressive=False, file_extension='mp4').order_by('resolution')[-1]
    title = video_track.title.replace('"', '')

    video_track.download(filename="video")
    audio_track.download(filename="audio")

    combine_tracks("video.mp4", "audio.mp4", title + ".mp4")

    # delete redundant video and audio tracks
    os.remove("video.mp4")
    os.remove("audio.mp4")

print("File successfully downloaded.")
