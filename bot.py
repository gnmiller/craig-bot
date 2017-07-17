#!/usr/bin/python3.6

import asyncio, json, urllib3, datetime, discord, dateutil
from apiclient.discovery import build
from datetime import date
from datetime import timedelta
from threading import Timer
import pdb
import dateutil.parser
import dateutil.relativedelta
import pytz

import os
path = os.path.dirname(os.path.realpath(__file__))
with open( path+'/settings.json' ) as f:
    data = json.load( f )

# init global vars...
client = discord.Client()
discord_token = data["discord"]["token"]
youtube_token = data["youtube"]["token"]
tmdb_token = data["tmdb"]["token"]
max_time = data["bot"]["timeout"]
prefix = data["bot"]["prefix"]
me = "BeeStingBot"
searched = False
results = {}
timer = None
search_time = datetime.datetime.now() - datetime.timedelta( days=90 )
search_msg = None
last_msg = None
squad = []
mode = ""


def write_log( log ):
    logfile = open( data["bot"]["logfile"], "a" )
    time_format = "%m/%d/%Y %H:%M:%S"
    now = date.today()
    time = now.strftime( time_format )
    logfile.seek( 0, 2 ) #EOF
    logfile.write( time+" :: "+log+"\n" )
    logfile.close()
    return

def search_helper():
    """reset search"""
    global searched
    global results 
    global timer
    global search_time
    global mode
    global search_msg
    search_time = None
    mode = ""
    searched = False
    results = {}
    timer = None
    search_msg = None
    return

def timeout():
    now = datetime.datetime.now()
    if( searched == False ):
        return False
    if( now > ( search_time + timedelta( seconds=max_time ) ) ):
        return True
    else:
        return False

class result:
    """simple container for search results"""
    name = ""
    id = -1

    def __init__(self,t,i):
        self.title = str(t)
        self.id = str(i)

    def set_title( self, t ):
        self.title = t

    def set_id( self, i ):
        self.id = i

class bee_sting_member():
    """container for discord member's and time"""
    def __init__(self, whoami):
        self.me = whoami
        self.time = datetime.datetime.now()

def youtube_search( term ):
    """Search using YouTube's API"""
    global searched
    global timer
    global results
    global search_time
    global mode

    if( timeout() == True ):
        return "Timeout!"
    elif( searched == True ):
        return "Search in progress still!"
    else:
        results = {}
        timer = None
        searched = False
        search_time  = None
        mode = "youtube"

    youtube = build( "youtube", "v3", developerKey=youtube_token )
    resp = youtube.search().list(
        q=term,
        part="id,snippet",
        maxResults=50
    ).execute()

    count = 0
    res_str = "```css\n"
    for res in resp.get( "items", [] ):
        if( res["id"]["kind"] == "youtube#video" ):
            count+=1
            res_str += str(count)+". "+res["snippet"]["title"]+"\n"
            title = res["snippet"]["title"]
            video_id = res["id"]["videoId"]
            vid = result( title, video_id )
            results[count] = vid
            if( count >= 10 ):
                break
        else:
            continue
    searched = True
    search_time = datetime.datetime.now()
    res_str+="\n```"
    return res_str

def get_got_time():
    """fetch time to next got episode"""
    cur = datetime.datetime.now()
    uri = "http://api.tvmaze.com/shows/82?embed=nextepisode"
    http = urllib3.PoolManager()
    response = http.request( 'GET', uri )
    data = json.loads( response.data.decode( 'utf-8' ) )
    next_ep = dateutil.parser.parse( data["_embedded"]["nextepisode"]["airstamp"] )
    cur = pytz.utc.localize( cur )
    diff = dateutil.relativedelta.relativedelta( next_ep, cur )
    print_str = "```css\nThere are ---\n"
    if( diff.months > 0 ):
        print_str+=str(diff.months)+" Months\n"
    if( diff.days > 0 ):
        print_str+=str(diff.days)+" Days\n"
    if( diff.minutes > 0 ):
        print_str+=str(diff.minutes)+" Minutes and\n"
    if( diff.seconds > 0 ):
        print_str+=str(diff.seconds)+" Seconds\n"
    print_str+="until the next Game of Thrones airs!\n\n```"
    return print_str

def the_squad():
    """fetch squadmate status"""
    global squad
    ret_str = ""
    count = 1
    ret_str = " \n| Where is The Squad |\n"
    for m in squad:
        ret_str += "|  <@"+m.me.id+"> --- "+str(m.me.status)+" --- "+m.time.strftime( "%m/%d %I:%M:%S %p")+"   |\n"
    ret_str += ""
    return ret_str

def get_squad():
    """propogate the squad array"""
    global squad
    add = False
    for u in client.get_all_members():
        add = False
        for r in u.roles:
            if r.name == "the_squad":
                add = True
                for s in squad:
                    if s.me.name == u.name:
                        add = False
        if add == True:                    
            m = bee_sting_member( u )
            squad.append( m )

def tmdb_search( term ):
    global searched
    global timer
    global results
    global search_time
    global mode

    if( timeout() == True ):
        return "Timeout!"
    elif( searched == True ):
        return "Search in progress still!"
    else:
        results = {}
        timer = None
        searched = False
        search_time  = None
        mode = "tmdb"
    
        uri = "https://api.themoviedb.org/3/search/movie?api_key="+tmdb_token+"&query="+term
        searched = True
        search_time = datetime.datetime.now()
        http = urllib3.PoolManager()
        response = http.request( 'GET', uri )
        data = json.loads( response.data.decode( 'utf-8' ) )
        count = 0
        res_str = "```css\n"
        for res in data.get( "results", [] ):
            title = res["title"]
            video_id = res["id"]
            rating = res["vote_average"]
            rating_count = res["vote_count"]
            year = res["release_date"][0:4]
            if( count >= 10 ):
                break
            count+=1
            res_str += str(count)+". "+title+" ("+str(year)+") -- "+str(rating)+"/10 ("+str(rating_count)+")\n"
            vid = result( title, video_id )
            results[count] = vid
        res_str += "```"
        return res_str

def ffxivdb_search( term ):
    global searched
    global timer
    global results
    global search_time
    global mdoe

    if( timeout() == True ):
        return "Timeout!"
    elif( searched == True ):
        return "Search still in progress!"
    else:
        results = {}
        timer = None
        searched = False
        search_time = None
        mode = "ff"

        uri = "https://api.xivdb.com/search?string="+term
        searched = True
        search_time = datetime.datetime.now()
        http = urllib3.PoolManager()
        response = http.request( 'GET', uri )
        data = json.loads( response.data.decode( 'utf-8' ) )
        count = 0
        res_str = ""
        import pdb
        pdb.set_trace()
        if( data.get( "characters", [] )["results"]["total"] == 1 ):
            res_str += "Only one result returned!\n"
            res_str += "https://api.xivdb.com/characters/"+str( data.get( "characters", [] )["results"]["id"] )+"\n"
            search_helper()
            return
        res_str = "```css\n"
        for res in data.get( "characters", [] ):
            name = res["results"]["name"]
            id = res["results"]["id"]
            server = res["results"]["server"]
            if( count >= 10 ):
                break
            count+=1
            res_str += str(count)+". "+name+" ("+server+")\n"
            tmp = result( name+" - ("+server+")", id )
            results[count] = tmp
        res_str += "```"
        return res_str

@client.event
async def on_member_join():
    global squad
    get_squad()

@client.event
async def on_member_update( before, after ):
    global squad
    timeout()
    for m in squad:
        if m.me.name == after.name:
            m.time = datetime.datetime.now()
            m.me = after

@client.event
async def on_ready():
    global squad
    write_log( "bot started!" )
    write_log( "user: "+client.user.name )
    write_log( "id: "+client.user.id )
    write_log( "----------------------" )
    get_squad()

@client.event
async def on_message( msg ):
    global searched
    global search_msg
    global last_msg

    if( msg.author.name.find( me ) >= 0 ):
        return 

        # check for prefix
    if( searched == True ):
        # check if sender matches whomever searched
        if( search_msg.author.name.find( msg.author.name ) != 0 ):
            return
        # check timeout
        if( timeout() == True ):
            search_helper()
            return
        # check int
        if ( msg.content.isdigit() == False ):
            return
        val = int( msg.content )
        # check range
        if( val > 10 or val < 0 ):
            return
        if( mode == "youtube" ):
            ret_uri = "Selected video -"+str(val)+"-\nTitle: "+results[val].name+"\nhttps://www.youtube.com/watch?v="+str(results[val].id)
        elif( mode == "tmdb" ):
            ret_uri = "Selected video -"+str(val)+"-\nTitle: "+results[val].name+"\nhttps://www.themoviedb.org/movie/"+str(results[val].id)
        elif( mode == "ff" ):
            ret_uri = "Selected character - "+str(val)+"-\nName: "+results[val].name+"\nhttps://api.xivdb.com/characters/"+str(results[val].id)
        last_msg = await client.edit_message( last_msg, ret_uri )
        search_helper()

    if( msg.content[:len(prefix)].find( prefix ) >= 0 ):
        cmd = msg.content[len(prefix):]
        args = cmd.split()
        if( args[0] == "yt" ):
            search_str = ""
            search_msg = msg

            for i in args[1:]:
                search_str+=i+" "
            last_msg = await client.send_message( msg.channel, youtube_search( search_str ) )
            return
        elif( args[0] == "got" ):
            last_msg = await client.send_message( msg.channel, get_got_time() )
            return
        elif( args[0] == "squad" ):
            last_msg = await client.send_message( msg.channel, the_squad() ) 
            return
        elif( args[0] == "movie" ):
            search_str = ""
            search_msg = msg

            for i in args[1:]:
                search_str += i+"+"
            last_msg = await client.send_message( msg.channel, tmdb_search( search_str ) )
            return
        elif( args[0] == "ff" ):
            search_str = ""
            search_msg = msg

            for i in args[1:]:
                search_str += i+"+"
            last_msg = await client.send_message( msg.channel, ffxivdb_search( search_str ) )
            return
        else:
            return

client.run( discord_token ) 
