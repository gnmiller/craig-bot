#!/usr/bin/python

import discord
from apiclient.discovery import build
import asyncio
import json
from datetime import date as date
from threading import Timer

with open( './settings.json' ) as f:
    data = json.load( f )

client = discord.Client()
discord_token = data["discord"]["token"]
youtube_token = data["youtube"]["token"]
prefix = data["bot"]["prefix"]
me = "BeeStingBot"

def write_log( log ):
    logfile = open( data["bot"]["logfile"], "a" )
    time_format = "%m/%d/%Y %H:%M:%S"
    now = date.today()
    time = now.strftime( time_format )
    logfile.seek( 0, 2 ) #EOF
    logfile.write( time+" :: "+log+"\n" )
    logfile.close()
    return

videos = []
v_ids = []
searched = False
timer = None
async def search_helper( msg ):
    searched = False
    videos = []
    ids = []
    timer = None
    print( "timeout!" )
    await client.send_message( msg.channel, "Timeout!" )
    return

async def youtube_search( term, msg ):
    if( searched == 1 ):
        return "Search in progress still!"

    youtube = build( "youtube", "v3", developerKey=youtube_token )
    resp = youtube.search().list(
        q=term,
        part="id,snippet",
        maxResults=10
    ).execute()

    count = 0
    res_str = ""
    for res in resp.get( "items", [] ):
        if( res["id"]["kind"] == "youtube#video" ):
            count+=1
            res_str += str(count)+". "+res["snippet"]["title"]+"\n"
            videos.append( "%s" % (res["snippet"]["title"] ) )
            v_ids.append( "%s" % (res["id"]["videoId"] ) )
            if( count == 10 ):
                break
        else:
            continue

    timer = Timer( 15.0, search_helper( msg ) )
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
    if( msg.content[:len(prefix)].find( prefix ) >= 0 ):
        cmd = msg.content[len(prefix):]
        args = cmd.split()
        if( args[0] == "yt" ):
            search_str = ""
            for i in args[1:]:
                search_str+=i+" "
            print( search_str )
            search_results = await youtube_search( search_str, msg )
            write_log( "Got results string: "+search_results )
            await client.send_message( msg.channel, "```css\n"+search_results+"\n```" )
            return
        else:
            write_log( "caught unknown cmd" )
            return

client.run( discord_token ) 
