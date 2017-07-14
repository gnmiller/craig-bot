#!/usr/bin/python

import discord
from apiclient.discovery import build
import asyncio
import json
from datetime import date
from datetime import timedelta
import datetime
from threading import Timer

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
search_time = -1

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
            search_helper( msg )
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
    res_str = ""
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
    return res_str


@client.event
async def on_ready():
    write_log( "bot started!" )
    write_log( "user: "+client.user.name )
    write_log( "id: "+client.user.id )
    write_log( "----------------------" )

@client.event
async def on_message( msg ):
    if( msg.author.name.find( me ) >= 0 ):
        return 

    # check for prefix
    import pdb
    pdb.set_trace()
    if( msg.content[:len(prefix)].find( prefix ) >= 0 ):
        cmd = msg.content[len(prefix):]
        args = cmd.split()
        if( args[0] == "yt" ):
            search_str = ""
            for i in args[1:]:
                search_str+=i+" "
            print( search_str )
            search_results = youtube_search( search_str )
            write_log( "Got results string: "+search_results )
            await client.send_message( msg.channel, "```css\n"+search_results+"\n```" )
            return
        elif( datetime.datetime.now() < search_time + timedelta( seconds=15 ) and searched == True ):
            val = int( args[0] )
            if( val > 10 or val < 0 ):
                await client.send_message( msg.channel, "Invalid selection!" )
            else:
                await client.send_message( msg.channel, videos[i].title )
        else:
            write_log( "caught unknown cmd" )
            return

client.run( discord_token ) 
