#!/usr/bin/env python3

from libopensonic.connection import Connection
from mutagen.flac import FLAC
import argparse
import sys


parser = argparse.ArgumentParser(description='Sync album ratings from subsonic to FLAC files.')
parser.add_argument('--host', dest='subsonic_host', action='store',
                    help='URL to subsonic server')
parser.add_argument('--user', dest='subsonic_user', action='store',
                    help='Subsonic user')
parser.add_argument('--password', dest='subsonic_password', action='store',
                    help='Subsonic password')
parser.add_argument('--port', dest='subsonic_port', action='store',
                    help='Subsonic port')
parser.add_argument('--dir', dest='music_dir', action='store',
                    help='Subsonic music base directory')

args = parser.parse_args()

if args.subsonic_host is None or args.subsonic_user is None or args.subsonic_port is None or args.music_dir is None:
    parser.print_help()
    sys.exit(1)

# We pass in the base url, the username, password, and port number
# Be sure to use https:// if this is an ssl connection!
conn = Connection(args.subsonic_host, args.subsonic_user, args.subsonic_password, args.subsonic_port)

offset = 0
album_ids = []
ratings = {}
while True:
    albums = conn.getAlbumList(ltype='alphabeticalByName', offset=offset, size=500)
    for a in albums:
        if a.user_rating != 0:
            album_ids.append(a.id)
            ratings[a.id]=a.user_rating
    if len(albums)<500:
        break
    offset+=500

for album_id in album_ids:
    album = conn.getAlbum(album_id=album_id)
    print(album.artist + ' - ' + album.name)
    for song in album.songs:
        file = FLAC(args.music_dir + song.path)
        file['ALBUMRATING'] = f'{ratings[album_id]}'
        file.save()
