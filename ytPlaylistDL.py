#!/usr/bin/env python3

import urllib.request
import urllib.error
import re
import sys
import time
import os
from pytube import YouTube
import whisper
import ffmpeg

class progressBar:
    def __init__(self, barlength=25):
        self.barlength = barlength
        self.position = 0
        self.longest = 0

    def print_progress(self, cur, total, start):
        currentper = cur / total
        elapsed = int(time.process_time() - start) + 1
        curbar = int(currentper * self.barlength)
        bar = '\r[' + '='.join(['' for _ in range(curbar)])  # Draws Progress
        bar += '>'
        bar += ' '.join(['' for _ in range(int(self.barlength - curbar))]) + '] '  # Pads remaining space
        bar += bytestostr(cur / elapsed) + '/s '  # Calculates Rate
        bar += getHumanTime((total - cur) * (elapsed / cur)) + ' left'  # Calculates Remaining time
        if len(bar) > self.longest:  # Keeps track of space to over write
            self.longest = len(bar)
            bar += ' '.join(['' for _ in range(self.longest - len(bar))])
        sys.stdout.write(bar)

    def print_end(self, *args):  # Clears Progress Bar
        sys.stdout.write('\r{0}\r'.format((' ' for _ in range(self.longest))))

def getHumanTime(sec):
    if sec >= 3600:  # Converts to Hours
        return '{0:d} hour(s)'.format(int(sec / 3600))
    elif sec >= 60:  # Converts to Minutes
        return '{0:d} minute(s)'.format(int(sec / 60))
    else:            # No Conversion
        return '{0:d} second(s)'.format(int(sec))

def bytestostr(bts):
    bts = float(bts)
    if bts >= 1024 ** 4:    # Converts to Terabytes
        terabytes = bts / 1024 ** 4
        size = '%.2fTb' % terabytes
    elif bts >= 1024 ** 3:  # Converts to Gigabytes
        gigabytes = bts / 1024 ** 3
        size = '%.2fGb' % gigabytes
    elif bts >= 1024 ** 2:  # Converts to Megabytes
        megabytes = bts / 1024 ** 2
        size = '%.2fMb' % megabytes
    elif bts >= 1024:       # Converts to Kilobytes
        kilobytes = bts / 1024
        size = '%.2fKb' % kilobytes
    else:                   # No Conversion
        size = '%.2fb' % bts
    return size

def getPageHtml(url):
    try:
        yTUBE = urllib.request.urlopen(url).read()
        return str(yTUBE)
    except urllib.error.URLError as e:
        print(e.reason)
        exit(1)

def getPlaylistUrlID(url):
    if 'list=' in url:
        eq_idx = url.index('=') + 1
        pl_id = url[eq_idx:]
        if '&' in url:
            amp = url.index('&')
            pl_id = url[eq_idx:amp]
        return pl_id   
    else:
        print(url, "is not a youtube playlist.")
        exit(1)

def getFinalVideoUrl(vid_urls):
    final_urls = []
    for vid_url in vid_urls:
        url_amp = len(vid_url)
        if '&' in vid_url:
            url_amp = vid_url.index('&')
        final_urls.append('http://www.youtube.com/' + vid_url[:url_amp])
    return final_urls

def getPlaylistVideoUrls(page_content, url):
    playlist_id = getPlaylistUrlID(url)

    vid_url_pat = re.compile(r'watch\?v=\S+?list=' + playlist_id)
    vid_url_matches = list(set(re.findall(vid_url_pat, page_content)))

    if vid_url_matches:
        final_vid_urls = getFinalVideoUrl(vid_url_matches)
        print("Found", len(final_vid_urls), "videos in playlist.")
        printUrls(final_vid_urls)
        return final_vid_urls
    else:
        print('No videos found.')
        exit(1)

def download_Video_Audio(video_path, audio_path, transcript_path, vid_url):
    try:
        yt = YouTube(vid_url)
    except Exception as e:
        print("Error:", str(e), "- Skipping Video with url '"+vid_url+"'.")
        return

    try:  # Tries to find the video in 720p
        video = yt.streams.filter(progressive=True, file_extension="mp4").first()
    except Exception:  # Sorts videos by resolution and picks the highest quality video if a 720p video doesn't exist
        video = sorted(yt.filter("mp4"), key=lambda video: int(video.resolution[:-1]), reverse=True)[0]

    print("Downloading", yt.title + " Video and Audio...")
    try:
        bar = progressBar()
        video.download(output_path=video_path)
        print("Successfully downloaded", yt.title, "!")
    except OSError:
        print(yt.title, "already exists in this directory! Skipping video...")

    video_file_path = os.path.join(video_path, video.default_filename)
    audio_file_path = os.path.join(audio_path, os.path.splitext(video.default_filename)[0] + '.mp3')

    try:
        # Convert video to audio
        convert_video_to_audio(video_file_path, audio_file_path)
        
        # Transcribe audio
        transcribe_audio(audio_file_path, transcript_path)

    except OSError as e:
        print(yt.title, "There is some problem with the file names:", str(e))

def convert_video_to_audio(video_path, audio_path):
    try:
        stream = ffmpeg.input(video_path)
        stream = ffmpeg.output(stream, audio_path, acodec='libmp3lame')
        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
        print("Successfully converted video to audio:", audio_path)
    except ffmpeg.Error as e:
        print(f"FFmpeg error converting video to audio {video_path}:")
        print(f"FFmpeg stdout: {e.stdout.decode('utf8')}")
        print(f"FFmpeg stderr: {e.stderr.decode('utf8')}")

def transcribe_audio(audio_path, transcript_path):
    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        transcript_file_path = os.path.join(transcript_path, os.path.splitext(os.path.basename(audio_path))[0] + ".txt")
        with open(transcript_file_path, "w", encoding="utf-8") as f:
            f.write(result["text"])
        print(f"Transcription complete for {audio_path}")
    except Exception as e:
        print(f"Error transcribing audio {audio_path}: {e}")

def printUrls(vid_urls):
    for url in vid_urls:
        print(url)
        time.sleep(0.04)

if __name__ == '__main__':
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print('USAGE: python ytPlaylistDL.py playlistURL OR python ytPlaylistDL.py playlistURL destPath')
        exit(1)
    else:
        url = sys.argv[1]
        base_directory = os.getcwd() if len(sys.argv) != 3 else sys.argv[2]

        # make directories if they don't exist
        video_directory = os.path.join(base_directory, 'videos')
        audio_directory = os.path.join(base_directory, 'audios')
        transcript_directory = os.path.join(base_directory, 'transcripts')
        
        try:
            os.makedirs(video_directory, exist_ok=True)
            os.makedirs(audio_directory, exist_ok=True)
            os.makedirs(transcript_directory, exist_ok=True)
        except OSError as e:
            print(e.reason)
            exit(1)

        if not url.startswith("http"):
            url = 'https://' + url

        playlist_page_content = getPageHtml(url)
        vid_urls_in_playlist = getPlaylistVideoUrls(playlist_page_content, url)

        # downloads videos and audios
        for vid_url in vid_urls_in_playlist:
            download_Video_Audio(video_directory, audio_directory, transcript_directory, vid_url)
            time.sleep(1)
