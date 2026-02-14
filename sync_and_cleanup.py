#!/usr/bin/env python3 -u

from libopensonic.connection import Connection
import argparse
import sys
import os
from mutagen.flac import FLAC

parser = argparse.ArgumentParser(description='Sync album ratings from subsonic to FLAC files and optionally delete 1-star albums.')
parser.add_argument('--dry-run', dest='dry_run', action='store_true',
                    help='Only print operations without executing them')

args = parser.parse_args()

subsonic_host = os.environ.get('SUBSONIC_HOST')
subsonic_user = os.environ.get('SUBSONIC_USER')
subsonic_password = os.environ.get('SUBSONIC_PASSWORD')
subsonic_port = os.environ.get('SUBSONIC_PORT')
music_dir = '/music'

if subsonic_host is None or subsonic_user is None or subsonic_port is None:
    print("Error: SUBSONIC_HOST, SUBSONIC_USER, and SUBSONIC_PORT environment variables must be set", flush=True)
    parser.print_help()
    sys.exit(1)

music_dir = music_dir.rstrip('/')

print(f"Connecting to {subsonic_host}...", flush=True)

conn = Connection(subsonic_host, subsonic_user, subsonic_password, subsonic_port)

import time
import socket

socket.setdefaulttimeout(10)

print(f"Connected, fetching albums...", flush=True)

offset = 0
albums_data = []
print("Fetching album list...", flush=True)
while True:
    try:
        albums = conn.getAlbumList(ltype='alphabeticalByName', offset=offset, size=500)
        print(f"Got {len(albums)} albums at offset {offset}", flush=True)
    except Exception as e:
        print(f"Error fetching albums: {e}", flush=True)
        break
    for a in albums:
        if a.user_rating is not None and a.user_rating > 0:
            albums_data.append({'id': a.id, 'rating': a.user_rating})
    if len(albums) < 500:
        break
    offset += 500

print(f"Found {len(albums_data)} albums with ratings, processing...", flush=True)

count = 0
for album_info in albums_data:
    try:
        album = conn.getAlbum(album_id=album_info['id'])
    except socket.timeout:
        print(f"Timeout getting album {album_info['id']}, skipping", flush=True)
        continue
    except Exception as e:
        print(f"Error getting album {album_info['id']}: {e}", flush=True)
        continue
    count += 1
    if count % 50 == 0:
        print(f"Processed {count}/{len(albums_data)} albums...", flush=True)
    if not album.songs:
        continue
    
    subsonic_path = album.songs[0].path
    
    album_path = os.path.join(music_dir, subsonic_path)
    album_dir = os.path.dirname(album_path)
    rating = album_info['rating']
    
    if rating == 1:
        if args.dry_run:
            print(f"[DRY RUN] Would delete: {album_dir}")
        else:
            print(f"Deleting: {album_dir}")
            try:
                for file in os.listdir(album_dir):
                    file_path = os.path.join(album_dir, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                os.rmdir(album_dir)
                print(f"Deleted: {album_dir}")
            except OSError as e:
                print(f"Error deleting {album_dir}: {e}")
    else:
        if not os.path.exists(album_dir):
            continue
        
        for file in os.listdir(album_dir):
            file_path = os.path.join(album_dir, file)
            if os.path.isfile(file_path) and file_path.lower().endswith('.flac'):
                try:
                    flac_file = FLAC(file_path)
                    current_rating = flac_file.get('ALBUMRATING', [None])[0]
                    if str(rating) != current_rating:
                        if args.dry_run:
                            print(f"[DRY RUN] Would write ALBUMRATING={rating} to {file_path}")
                        else:
                            flac_file['ALBUMRATING'] = str(rating)
                            flac_file.save()
                            print(f"Wrote ALBUMRATING={rating} to {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
