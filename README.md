# ytdownloader

A simple YouTube downloader written in Python.

## Installation

Get [FFmpeg](https://ffmpeg.org/download.html) and run the following commands:

```
python -m pip install git+https://github.com/nficano/pytube
git clone https://github.com/sgrontflix/ytdownloader
```

or 

```
python3 -m pip install git+https://github.com/nficano/pytube
git clone https://github.com/sgrontflix/ytdownloader
```

### For Windows users

Make sure to install [Python](https://www.python.org/downloads/) and [Git](https://gitforwindows.org/) before downloading FFmpeg and executing the commands above.

Check `Add Python to environment variables` in `Advanced Options` when installing Python.

You can leave everything on default when installing Git.

After downloading an FFmpeg Windows build from the official website or directly from [here](https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z), unpack the archive and put the extracted folder inside `ytdownloader`. Your `ffmpeg_path` will be `<NAME_OF_EXTRACTED_FOLDER>\bin\ffmpeg.exe`.

### For Linux users

You can install everything you need from the command line.

After installing FFmpeg, run `whereis ffmpeg` to get the full installation path. It should be something like `/usr/bin/ffmpeg`.

## Usage

`python main.py ffmpeg_path url`

or

`python3 main.py ffmpeg_path url`
