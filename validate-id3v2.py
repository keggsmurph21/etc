#!/usr/bin/env python3
'''
validate-id3v2.py
Kevin Murphy 3/25/2018

This program updates some id3v2 metadata fields for a given list of artists in
a specified directory.
'''

import argparse
import eyed3 # sudo -H pip2 install eyeD3
import json
import logging
import os
import pygn  # curl https://raw.githubusercontent.com/cweichen/pygn/master/pygn.py > pygn.py
import requests
import shutil

ALBUM_ART_FILE_NAME = 'front.jpeg'
VERBOSITY = 3

def check_errors( data, artist, album ):
    return data['album_artist_name'].lower() != artist.lower() or data['album_title'].lower() != album.lower()

def check_metadata( client_id, user_id, path, errors=[], fix_errors=False ):
    for root, dirs, files in os.walk(path):

        save_changes = True

        if dirs == []: # album
            artist = os.path.basename(os.path.dirname(root))
            album  = os.path.basename(root)
            album_path = os.path.join( path, album )
            log( ' - %s' % album, 'WARNING' )

            data = pygn.search( clientID=client_id, userID=user_id, artist=artist, album=album )

            log( json.dumps(data, indent=3 ), 'DEBUG' )

            if check_errors( data, artist, album ):
                if fix_errors:
                    resolve_errors( data, artist, album )
                else:
                    log( ' >>ERROR', 'INFO' )
                    errors.append( path )
                    save_changes = False

            if save_changes:
                download_album_art( album_path, data['album_art_url'] )
                for f in files:
                    update_metadata( album_path, f, data )

        else: # artist
            artist  = os.path.basename(root)
            log( '\n%s' % artist, 'WARNING' )

def download_album_art( album_path, url ):
    global ALBUM_ART_FILE_NAME

    if url != '':

        res = requests.get( url, stream=True )
        if res.status_code == 200:
            res.raw.decode_content = True
            album_art_path = os.path.join( album_path, ALBUM_ART_FILE_NAME )
            with open( album_art_path, 'wb' ) as f:
                shutil.copyfileobj( res.raw, f )
            return

    log( '    unable to download album art', 'INFO' )

def get_genre( data ):
    genre = ''
    for genre_item in data['genre']:
        genre += data['genre'][genre_item]['TEXT'] + '; '
    return genre[:-2]

def log( msg, level_string='INFO' ):

    level_strings = ['CRITICAL','ERROR','WARNING','INFO','DEBUG']

    level = level_strings.index(level_string) if level_string in level_strings else 5
    if level > VERBOSITY:
        return
    elif level < 2:
        print( '%s: %s' % (level_string, msg) )
    else:
        print( msg )

def resolve_error( data, field ):
    data_field = 'album_artist_name' if field=='ARTIST' else 'album_title'
    res = input( 'change %s (to `%s`)? ' % (field, data[data_field]) )

    if res == '':
        log( 'changed %s to `%s`' % (field, data[data_field]), 'DEBUG' )
        return True
    elif res == '/':
        log( 'skipping...', 'DEBUG' )
        return None
    else:
        log( 'changed %s to `%s`' % (field, res), 'DEBUG' )
        data[data_field] = res
        return True

def resolve_errors( data, artist, album ):
    if data['album_artist_name'].lower() != artist.lower():
        if resolve_error( data, 'ARTIST' ) == None:
            return None
    if data['album_title'].lower() != album.lower():
        if resolve_error( data, 'ALBUM' ) == None:
            return None
    return True

def set_verbosity( args ):
    global VERBOSITY
    VERBOSITY = 0 if args.quiet else args.verbose

def update_metadata( album_path, file_name, data ):
    global ALBUM_ART_FILE_NAME

    file_path = os.path.join( album_path, file_name )
    file_data = eyed3.load( file_path )
    if file_data == None: # whatever eyed3 can't load
        return

    file_data = file_data.tag

    file_data.artist        = data['album_artist_name']
    file_data.album_artist  = data['album_artist_name']
    file_data.album         = data['album_title']

    year = data['album_year']
    if len(year):
        file_data.original_release_date = year

    file_data.genre = get_genre(data)

    album_art_path = os.path.join( album_path, ALBUM_ART_FILE_NAME )
    if os.path.exists( album_art_path ):
        album_art_data = open( album_art_path, 'rb' ).read()
        file_data.images.set(3, album_art_data, 'image/jpeg')

    try:
        file_data.save()
    except (eyed3.id3.tag.TagException, NotImplementedError):
        file_data.save(version=(2,3,0))

def validate_path(path, require_valid=False):
    if os.path.exists( path ):
        return path
    log( 'unable to resolve path: %s' % path, 'ERROR' )
    if require_valid:
        exit(1)

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument( '-a', '--artists', default='artists.txt', help='newline-separated line of artists to be evaluated (default=`artists.txt`)' )
    parser.add_argument( '-g', '--gnid', default='2016435791-02CA61403E3EB62723584D41E59C8455', help='gracenote client id' )
    parser.add_argument( '-q', '--quiet', action='store_true' )
    parser.add_argument( '-s', '--source', default='/Volumes/ /music/iTunes/iTunes Music/Music', help='path to music library' )
    parser.add_argument( '-v', '--verbose', action='count', default=2 )
    args = parser.parse_args()

    set_verbosity( args )

    eyed3.log.setLevel(logging.ERROR)
    user_id = pygn.register( args.gnid )
    src = validate_path( args.source, require_valid=True )

    errors = []

    with open( args.artists ) as f:
        for artist in f.readlines():

            artist_src_dir = validate_path( os.path.join( src, artist.strip() ) )
            check_metadata( args.gnid, user_id, artist_src_dir, errors=errors, fix_errors=False )

    if len(errors):
        log( '\n-----------\nRESOLVE ERRORS: enter `/` to skip, `` to accept changes, or new value', 'CRITICAL' )
    for err_path in errors:
        check_metadata( args.gnid, user_id, err_path, errors=[], fix_errors=True )

main()
