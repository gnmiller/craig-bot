import json, os, asyncio

# functions...
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
pfx = settings['bot']['prefix']

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

import omdb
def omdb_search( term, token, **kwargs ):
    omdb.set_default( 'apikey', token )
    """Return a list containing tuples of (film name, title, year, rating, id)"""
    try:
        res = omdb.search( term )
        ret = []
        count = 0
        ok_types = ['movie','series','episode'] # ignore games, etc
        for r in res:
            if r['type'] in ok_types:
                ret.append( ( r['title'], r['year'], r['imdb_id'] ) )
                count+=1
        if len(ret) <= 0:
            return -1
        else:
            return ret
    except:
        print( "help!" )
        return -1


def ck_cmd( msg, cmd ):
    """Checks if the first n characters of msg contain cmd. Should not contain the bot prefix when passed in.
    msg: String to search in..
    cmd: String to search for."""
    return cmd in msg[0:len(cmd)]

def help():
    """Print help string...."""
    path = os.path.dirname( os.path.realpath( __file__ ))
    with open( '{}/help.json'.format( path ) ) as f:
        help_strings = json.load( f )
    f.close()
    out_str = ''
    for e in help_strings:
        out_str+='{}\n'.format( help_strings[e].format( pfx ) )
    return out_str
