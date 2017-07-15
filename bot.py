#!/usr/bin/python

import asyncio, json, urllib3, datetime, discord, dateutil
from apiclient.discovery import build
from datetime import date
from datetime import timedelta
from threading import Timer
import pdb
import dateutil.parser
import dateutil.relativedelta

with open( './settings.json' ) as f:
    data = json.load( f )

# init global vars...
client = discord.Client()
discord_token = data["discord"]["token"]
youtube_token = data["youtube"]["token"]
prefix = data["bot"]["prefix"]
me = "BeeStingBot"
searched = False
videos = {}
timer = None
search_time = datetime.datetime.now() - datetime.timedelta( days=90 )
search_msg = None
last_msg = None
squad = []


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
    global videos
    global timer
    global search_time
    global search_msg
    search_time = None
    searched = False
    videos = {}
    timer = None
    search_msg = None
    return

class yt_video:
    """simple container for yt video data"""
    title = ""
    video_id = -1

    def __init__(self,t,i):
        self.title = str(t)
        self.video_id = str(i)

    def set_title( self, t ):
        self.title = t

    def set_id( self, i ):
        self.video_id = i

class bee_sting_member():
    """container for discord member's and time"""
    def __init__(self, whoami):
        self.me = whoami
        self.time = datetime.datetime.now()

def youtube_search( term ):
    """Search using YouTube's API"""
    global searched
    global timer
    global videos
    global search_time

    if( searched == True ):
        if( datetime.datetime.now() > search_time + timedelta( seconds=15 ) ):
            search_helper()
            return "Timeout!"
        else:
            return "Search in progress still!"
    else:
        videos = {}
        timer = None
        searched = False
        search_time  = None

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
            vid = yt_video( title, video_id )
            videos[count] = vid
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
    next_ep = next_ep.replace( tzinfo=None )
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

@client.event
async def on_member_join():
    global squad
    get_squad()

@client.event
async def on_member_update( before, after ):
    global squad
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
        cur = datetime.datetime.now()
        # check if sender matches whomever searched
        if( search_msg.author.name.find( msg.author.name ) != 0 ):
            return
        # check timeout
        if( cur > (search_time + timedelta( seconds=15 ) )):
            search_helper()
            return
        # check int
        if ( msg.content.isdigit() == False ):
            await client.send_message( msg.channel, "Invalid selection!" )
            return
        val = int( msg.content )
        # check range
        if( val > 10 or val < 0 ):
            await client.send_message( msg.channel, "Invalid selection!" )
            return
        ret_uri = "https://www.youtube.com/watch?v="+videos[val].video_id
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
        elif( args[0] == "squad" ):
            last_msg = await client.send_message( msg.channel, the_squad() ) 
        else:
            write_log( "caught unknown cmd" )
            return

client.run( discord_token ) 
