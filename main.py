import os
import re
from pytube import YouTube
from moviepy import editor as mpe


def youtube_url_validation(url):
    youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)' \
                    r'\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'

    youtube_regex_match = re.match(youtube_regex, url)
    if youtube_regex_match:
        return youtube_regex_match

    return youtube_regex_match


def combine(video_file, audio_file, out_file, fps=25):
    video = mpe.VideoFileClip(video_file)
    audio = mpe.AudioFileClip(audio_file)
    out = video.set_audio(audio)
    out.write_videofile(out_file, fps=fps)

    # close reader to avoid PermissionError: [WinError 32]
    video.close()
    audio.close()
    out.close()


while True:
    yt_url = input("\nEnter the URL: ")
    yt_url = yt_url.strip()

    if not yt_url or not youtube_url_validation(yt_url):
        print("Please, provide a valid YouTube URL.")
    else:
        break

while True:
    audio_only = input("\nDo you want to only download the audio? (y/n): ")
    audio_only = audio_only.strip().upper()

    if audio_only == "Y" or audio_only == "N":
        break
    else:
        print("Please, only enter 'y' or 'n'.")

yt = YouTube(yt_url)
audio_track = yt.streams.filter(only_audio=True, file_extension='mp4').order_by('bitrate')[-1]

if audio_only == "Y":
    audio_track.download()
else:
    video_track = yt.streams.filter(progressive=False, file_extension='mp4').order_by('resolution')[-1]
    title = video_track.title.replace('"', '')

    video_track.download(filename="video")
    audio_track.download(filename="audio")

    combine("video.mp4", "audio.mp4", title + ".mp4")

    os.remove("video.mp4")
    os.remove("audio.mp4")

print("File successfully downloaded.")
