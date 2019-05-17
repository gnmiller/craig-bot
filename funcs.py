import json, os, asyncio

def chk_pfx( msg, p ):
    """check if msg content contains the given prefix"""
    return msg[:len(p)] == p

def get_pfx( msg, p ):
    return msg[:len(p)]

def get_settings( file ):
    """Load file as a json and return it"""
    path = os.path.dirname( os.path.realpath( __file__ ))
    with open( '{}/{}'.format(path,file) ) as f:
        settings = json.load( f )
    f.close()
    return settings
settings = get_settings( 'settings.json' )

import logging
def setup_logs( file ):
    """Setup logging"""
    LOG_LEVEL = logging.DEBUG
    path = '{}/var'.format( os.path.dirname( os.path.realpath( __file__ )) )
    try:
        os.mkdir( path )
    except FileExistsError:
        # do nothing...
        pass
    l = logging.getLogger( 'craig-bot' )
    l.setLevel( LOG_LEVEL )
    fh = logging.FileHandler( '{}/bot.log'.format( path ) )
    fh.setLevel( LOG_LEVEL )
    f = logging.Formatter( '%(asctime)s - %(name)s - %(levelname)s - %(message)s' )
    fh.setFormatter(f)
    l.addHandler( fh )
    return l

from apiclient.discovery import build
def yt_search( term, token ):
    """Return a list contains tuples with (title,id) for YT videos"""
    try:
        yt = build( 'youtube', 'v3', developerKey=token )
        resp = yt.search().list( q=term, part='id,snippet', maxResults=10 ).execute()
    except HttpError:
        print( 'oops' )
        return
    result = []
    for r in resp.get( 'items', [] ):
        if r['id']['kind'] == 'youtube#video':
            result.append( (r['snippet']['title'], r['id']['videoId'] ) )
    return result

