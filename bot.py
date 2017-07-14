#!/usr/bin/python

import asyncio, json, urllib3, datetime, discord, dateutil
from apiclient.discovery import build
from datetime import date
from datetime import timedelta
from threading import Timer
import dateutil.parser
import dateutil.relativedelta

with open( './settings.json' ) as f:
    data = json.load( f )

client = discord.Client()
discord_token = data["discord"]["token"]
youtube_token = data["youtube"]["token"]
prefix = data["bot"]["prefix"]
me = "BeeStingBot"
searched = False
videos = {}
timer = None
search_time = datetime.datetime.now() - datetime.timedelta( days=90 )

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
    global searched
    global videos
    global timer
    global search_time
    search_time = None
    searched = False
    videos = {}
    timer = None
    print( "timeout!" )
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
        
def youtube_search( term ):
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

@client.event
async def on_ready():
    write_log( "bot started!" )
    write_log( "user: "+client.user.name )
    write_log( "id: "+client.user.id )
    write_log( "----------------------" )

@client.event
async def on_message( msg ):
    global searched
    if( msg.author.name.find( me ) >= 0 ):
        return 

        # check for prefix
    if( searched == True ):
        cur = datetime.datetime.now()
        if( cur > (search_time + timedelta( seconds=15 ) )):
            print("timeout")
            search_helper()
            return
        if ( msg.content.isdigit() == False ):
            await client.send_message( msg.channel, "Invalid selection!" )
            return
        val = int( msg.content )
        if( val > 10 or val < 0 ):
            await client.send_message( msg.channel, "Invalid selection!" )
            return
        await client.send_message( msg.channel, videos[val].title )
        search_helper()

    if( msg.content[:len(prefix)].find( prefix ) >= 0 ):
        cmd = msg.content[len(prefix):]
        args = cmd.split()
        if( args[0] == "yt" ):
            search_str = ""
            for i in args[1:]:
                search_str+=i+" "
            await client.send_message( msg.channel, youtube_search( search_str ) )
            return
        elif( args[0] == "got" ):
            await client.send_message( msg.channel, get_got_time() )
        else:
            write_log( "caught unknown cmd" )
            return

client.run( discord_token ) 
