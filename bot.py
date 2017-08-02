#!/usr/bin/python3.6

import discord, asyncio, pytz, datetime, os, json, funcs
from server import bs_server
import pdb

path = os.path.dirname(os.path.realpath(__file__))
with open( path+'/settings.json' ) as f:
    settings = json.load( f )

client = discord.Client()
discord_key = settings["discord"]["token"]
youtube_key = settings["youtube"]["token"]
tmdb_key = settings["tmdb"]["token"]
prefix = settings["bot"]["prefix"]
timeout_val = settings["bot"]["timeout"]
date_str = "%m/%d/%y %I:%M %p"


servers = []
@client.event
async def on_ready():
    for s in client.servers:
        servers.append( bs_server( client, s, timeout_val ) )
    await client.change_presence( game=discord.Game( name="indev build" ) )
    print( "startup finished\n" )
    
@client.event
async def on_message( msg ):
    cur_serv = None
    for s in servers:
        if s.server == msg.server:
            cur_serv = s
    if msg.author == client.user:
        cur_serv.queue_msg( msg )
    now = pytz.utc.localize( datetime.datetime.now() )
    p = msg.content[:len(prefix)]
    args = msg.content[len(prefix):].split()
    if p == prefix:
        cur_serv.queue_cmd( msg )
        if args[0] == "yt":
            temp = await cur_serv.search( query_string( args ), "yt", youtube_key )
            return
        if args[0] == "tmdb":
            temp = await cur_serv.search( query_string( args ), "tmdb", tmdb_key )
            return
        if args[0] == "whoami":
            temp = await whoami( cur_serv, msg )
            return
        if args[0] == "got":
            temp = get_got_time()
            await client.send_message( msg.channel, temp )
            return
        return
    elif cur_serv.busy == True:
        if cur_serv.mode == "search":
            if cur_serv.helper.results == None:
                print( "Results error!\n" )
            if not msg.content.isdigit():
                return
            for i in range( 1, 10 ):
                if i == int(msg.content):
                    await cur_serv.get_res( i )
                    return
            return
        
def query_string( content ):
    query = ""
    for i in range( 1, len(content) ):
        query += content[i]+"+"
    query = query[:len(query)-1]
    return query

async def whoami( serv, msg ):
    msg_str = "```Username: {}\nID: {}\nAuth Level: {}\n```".format( msg.author.name, msg.author.id, serv.get_auth( msg.author ) )
    serv.queue_cmd( msg )
    return await client.send_message( msg.channel, msg_str )

client.run( discord_key )
