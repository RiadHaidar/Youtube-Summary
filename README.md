# Youtube-Summary
A simple script to download all videos in a youtube playlist (720p quality), convert them to audio and transcripts

### Requirements:

## python3 -m venv venv
## source venv/bin/activate

```bash

$ pip3 install pytube, FFmpeg

 git clone https://github.com/tdietert/youtubePlaylistDL.git

```

### Usage:

```bash
$ python ytPlaylistDL.py <playlistURL>
```
```bash
$ python ytPlaylistDL.py <playlistURL> <destinationPath>
```

### Example:
---
Say I'd like to download all videos in the playlist "FOMH 2015" (a music channel I like on youtube), found at URL 
https://www.youtube.com/playlist?list=PLVJcUspOFG-Np-YotXlPviRUK_MKyvwId, and put them in a music folder named
~/Music/FOMH. This is how I would do that:

```bash
$ python ytPlaylistDL.py https://www.youtube.com/playlist?list=PLVJcUspOFG-Np-YotXlPviRUK_MKyvwId ~/Music/FOMH
```
