# Subsonic utils

This repo contains some utilities for subsonic servers.

## Setup
Install the dependenies in `requirements.txt`.

## sync_album_ratings.py
Reads user album ratings and writes them to an `ALBUMRATING` tag. Only flac
files are supported. Run `./sync_album_ratings.py -h` for documentation.

## delete_1_star_albums.py
Deletes albums with a 1 star rating from the file system.

**Warning**: this script deletes every file in the same directory as the first
song of an album. This means that if you keep two albums in the same directory,
both would get deleted even though only one had the 1 star rating. It also
means that any files besides the music files (covers, text files, etc) will
also get deleted.

The script will recursively delete the empty album folder and its parent dirs.
So if you maintain a structure like `artist/album/01 song.flac`, the artist dir
will be automatically removed if their last album was removed.
