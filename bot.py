#!/usr/bin/python3.6

import discord, asyncio, pytz, datetime, os, json, youtube_dl
from discord.utils import find
from funcs import *
from funcs import bs_now as bnow
from dateutil import relativedelta
from server import bs_server
import pdb
import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='var/discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

path = os.path.dirname(os.path.realpath(__file__))
with open( path+'/settings.json' ) as f:
    settings = json.load( f )

client = discord.Client()
discord_key = settings["discord"]["token"]
youtube_key = settings["youtube"]["token"]
tmdb_key = settings["tmdb"]["token"]
prefix = settings["bot"]["prefix"]
timeout_val = settings["bot"]["timeout"]
max_msg = settings["bot"]["stored_msg"]
date_str = "%m/%d/%y %I:%M %p"
f.close()
if not discord.opus.is_loaded():
    discord.opus.load_opus( )

servers = []
@client.event
async def on_ready():
    print( "beginning startup" )
    for s in client.servers:
        servers.append( bs_server( client, s, timeout_val, max_msg ) )
        print( "new server: {} -- {}".format( s.name, s.id ) )
    temp = discord.Game( name="deez nuts" ) 
    with open( path+"/var/bot.pid", mode='w' ) as pid_file:
        print( "bot starting with pid={}".format( str( os.getpid() ) ) )
        pid_file.write( str( os.getpid()) )
        pid_file.close()
    await client.change_presence( game=temp )
    print( "startup finished" )
    
@client.event
async def on_server_join( server ):
    print( "new server!" )
    for s in servers:
        if s == server:
            return
    servers.append( bs_server( client, server, timeout_val, max_msg ) )
    return

@client.event
async def on_member_update( before, after ):
    for s in servers:
        for u in s.users:
            if u == after.id:
                s.users[u].state = after.status
                s.users[u].last = bnow()
    return

@client.event
async def on_message_edit( before, after ):
    for s in servers:
        if s.server == before.server:
            cur_serv = s
    if s.busy:
        return
    t = relativedelta.relativedelta( seconds = 90 )
    for msg in s.cmd_q:
        if msg.content.lower() == before.content.lower() and msg.author == before.author and (msg.timestamp + t) > after.timestamp:
            return
        else:
            await on_message( after )
            return
            
@client.event
async def on_message( msg ):
    cur_serv = None
    for s in servers:
        if s.server == msg.server:
            cur_serv = s
    #ignore PMs/etc
    if cur_serv == None:
        return
    if msg.author == client.user:
        cur_serv.queue_msg( msg )
    if msg.content == client.user.mention:
        await client.send_message( msg.channel, "Sorry, I don't normally respond to mentions! You can use {}help or {}h to get a PM of what I an do!".format( prefix, prefix ) )
    now = bnow()
    p = msg.content[:len(prefix)]
    args = msg.content[len(prefix):].split()
    if p == prefix:
        for a in args:
            a = a.lower()
        cur_serv.queue_cmd( msg )
        al = cur_serv.get_auth( msg.author )
        if args[0] == "help" or args[0] == "h":
            await client.send_message( msg.author, help_str( prefix, al ) )
            return
        if args[0] == "yt":
            temp = await cur_serv.search( query_string( args ), "yt", youtube_key )
            return
        if args[0] == "tmdb":
            temp = await cur_serv.search( query_string( args ), "tmdb", tmdb_key )
            return
        if args[0] == "got":
            temp = get_got_time()
            await client.send_message( msg.channel, temp )
            return
        if args[0] == "8ball":
            if len( args ) < 2:
                await client.send_message( msg.channel, "You need to ask a question!\n" )
                return
            temp = magic_8ball()
            p_str = "```smalltalk\nYou asked: {}\nThe Magic 8-Ball says: {}```\n".format( msg.content[7:], temp )
            await client.send_message( msg.channel, p_str )
            return
        if args[0] == "status":
            if al > 3:
                await client.send_message( msg.channel, creat_time() )
                return
            else:
                await client.send_message( msg.channel, "You are not authorized for this command. Required: 3 ({})\n".format( str( al ) ) )
                return
        if args[0] == "set_game":
            if al < 1:
                await client.send_message( msg.channel, "You are not authorized.\n" )
                return
            if len( args ) < 2:
                await client.send_message( msg.channel, "You need to specify a message for the game!\n" )
                return
            game_str = ""
            for i in range( 1, len( args ) ):
                game_str += args[i]+" "
            game_str = game_str[:len(game_str)-1]
            await client.change_presence( game=discord.Game( name=game_str ) )
            await client.send_message( msg.channel, "Setting now playing to: {}\n".format( game_str ) )
            return
        if args[0] == "save":
            if not al == 5:
                await client.send_message( msg.channel, "You are not authorized.\n" )
                return
            if len( args ) == 1:
                file = "./authorized.json"
            else:
                # try to avoid naughty people
                file = "./"+(args[1].split("/")[0])
            write_auth( servers, file )
            await client.send_message( msg.channel, "```Writing out the current authentication data to the file: "+file+"```" )
            return
        if args[0] == "add":
            if len( args ) <= 2:
                await client.send_message( msg.channel, "```Usage: {}add <user> <level> -- User may be a mention, name or ID```".format( prefix ) )
                return
            if not al == 5 or al < int(args[2]): #level 5 can add any otherwise <=
                await client.send_message( msg.channel, "```You cannot add a user with higher auth level than yourself!```" )
                return
            user = find_user( args[1], cur_serv.me.members )
            if user == None:
                await client.send_message( msg.channel, "```Couldn't find user by the name of: {}```".format( args[1] ) )
                return
            for u in cur_serv.users:
                if cur_serv.users[u].user.id == user.id:
                    cur_serv.add_auth( cur_serv.users[u].user, args[2] )
                    await client.send_message( msg.channel, "```Adding {} to the current server's auth list at level {}.\n```".format( user.name, args[2] ) )
                    return
            await client.send_message( msg.channel, "```Failed to add {} to the current server's auth list.\n```".format( args[1] ))
            return
        if args[0] == "del":
            if len(args) < 2:
                await client.send_message( msg.channel, "```Usage {}del <user> -- User may be a mention, name or ID```")
                return
            user = find_user( args[1], cur_serv.me.members )
            if user == None:
                await client.send_message( msg.channel, "```Couldn't find user by the name of: {}\n```".format( args[1] ) )
                return
            if al < cur_serv.get_auth( user ) or not al == 5:
                await client.send_message( msg.channel, "```You are not authorized\n" )
                return
            if not user.id in cur_serv.auth:
                await client.send_message( msg.channel, "```Doesn't look like {} is authorized yet.\n```".format( user.name ))
                return
            cur_serv.auth.pop(user.id, None) #destroy the key
            await client.send_message( msg.channel, "```De-authorizing {} ({})\n```".format( user.name, user.id ) )
            return
        if args[0] == "auth":
            print_str = print_auth( cur_serv.list_auth() )
            await client.send_message( msg.channel, print_str )
            return
        if args[0] == "eval":
            func = build_func( args )
            if func == "2+2-1":
                await client.send_message( msg.channel, "```2 plus 2 is 4, 4 minus 1 that's 3. Quick mafs!```" )
                return
            ret = eval( func )
            if ret == None:
                await client.send_message( msg.channel, "```Operation not supported!\n" )
                return
            await client.send_message( msg.channel, "```Evaluated: {}\nResult: {}\n```".format( func, ret ) )
            return
        if args[0] == "info" or args[0] == "whoami":
            if args[0] == "whoami":
                args = [ "info", msg.author.name ]
            if len(args) != 2:
                await client.send_message( msg.channel, "```Usage {}info <user> -- User may be a mention, id or name.\n```".format( p ))
                return
            user = find_bs_user( args[1], cur_serv )
            if user == None:
                await client.send_message( msg.channel, "```Couldn't find user by the name of: {}\n```".format( args[1] ) )
                return
            await client.send_message( msg.channel, "Info for -- {}\n```smalltalk\nUser: {}\nAuth Level: {}\nStatus: {}\nSince: {}\n```".format( user.user.mention, user.user.name, cur_serv.get_auth( user.user ), user.state, user.last.strftime( date_str ) ) )
            return
        if args[0] == "join":
            if( al < 3 ):
                await client.send_message( msg.channel, "```You are not authorized.\n```" )
                return
            if len(args) != 2:
                await client.send_message( msg.channel, "```Usage {}join <channel>```" )
                return
            chan_name = args[1]
            for c in cur_serv.me.channels:
                if c.name.lower() == chan_name.lower() and c.type.name == "voice":
                    if cur_serv.voice == None:
                        cur_serv.voice = await client.join_voice_channel( c )
                        await client.send_message( msg.channel, "```Bot is now joining: {} at the request of {}\n```".format( c.name, msg.author.name ) )
                    else:
                        await client.send_message( msg.channel, "```Bot is moving to: {} at the request of {}\n```".format( c.name, msg.author.name ) )
                        await cur_serv.voice.move_to( c )
                    return
        if args[0] == "leave":
            if( al < 3 ):
                await client.send_message( msg.channel, "```You are not authorized.\n```" )
                return
            cur_serv.voice.disconnect()
            await client.send_message( msg.channel, "```Bot is disconnecting from voice.\n```" )
            return
        if args[0] == "play":
            if al < 1:
                await client.send_message( msg.channel, "```You are not authorized.\n```" )
                return
            if len(args) == 1:
                await client.send_message( msg.channel, "```Usage {}play <yt_link>.\n```".format( p ))
                return
            if cur_serv.voice == None:
                return
            if cur_serv.stream == None:
                cur_serv.stream = await cur_serv.voice.create_ytdl_player( args[1] )
                cur_serv.stream.start()
                title_str = "Now playing: {}".format( cur_serv.stream.title )
                await client.change_presence( game=discord.Game( name=title_str ) )
                await client.send_message( msg.channel, "```{}```".format( title_str ) )
                await client.delete_message( msg )
                return
            else:
                if not cur_serv.voice == None and not cur_serv.stream.is_playing():
                    cur_serv.stream = cur_serv.voice.create_ytdl_player( args[1] )
                    cur_serv.stream.start()
                    title_str = "Now playing: {}".format( cur_serv.stream.title )
                    await client.change_presence( game=discord.Game( name=title_str ) )
                    await client.send_message( msg.channel, "```{}```".format( title_str ) )
                    await client.delete_message( msg )
                    return
                else:
                    await client.send_message( msg.channel, "```The current song is still playing, try again in a bit!\n```" )
                    return
        if args[0] == "stop":
            if al < 1:
                await client.send_message( msg.channel, "```You are not authorized.\n```" )
                return
            if not cur_serv.stream == None and not cur_serv.stream.is_playing():
                await client.send_message( msg.channel, "```No song playing.\n```" )
                return
            await client.send_message( msg.channel, "```Stopping playback.\n```" )
            cur_serv.stream.stop()
            cur_serv.stream = None
            await client.change_presence( game=discord.Game( name="Now Playing: None" ) )
            return
        if args[0] == "region":
            if al < 4:
                await client.send_message( msg.channel, "```You are not authorized.\n```" )
                return
            valid = ["us-west", "us-east", "us-central", "eu-west", "eu-central", "singapore", "london", "sydney", "amsterdam", "frankfurt", "brazil"]
            cur_reg = cur_serv.me.region
            if len(args) != 2:
                await client.send_message( msg.channel, "```Usage: {}region <new_region> Valid Selections are: {}```".format( p, ", ".join(valid)  ) )
                await client.send_message( msg.channel, "```Current region: {}.\n```".format( cur_serv.me.region ) )
                return
            req_reg = args[1].lower()
            if req_reg not in valid:
                await client.send_message( msg.channel, "```Invalid selection. Please choose from the following: {}```".format( ", ".join(valid) ) )
                return
            await client.send_message( msg.channel, "```Changing current region from {} to {}.\n```".format( cur_reg, req_reg ) )
            await client.edit_server( cur_serv.me, region=req_reg )
            await client.send_message( msg.channel, "```Region is now: {}.\n```".format( req_reg ) )
            return
        if args[0] == "mansnothot":
            await client.send_message( msg.channel, "https://www.youtube.com/watch?v=3M_5oYU-IsU" )
            return
    elif cur_serv.busy == True:
        if cur_serv.mode == "search":
            if cur_serv.helper.results == None:
                return
            if not msg.content.isdigit():
                return
            for i in range( 1, 10 ):
                if i == int(msg.content):
                    await cur_serv.get_res( i )
                    return
            return

client.run( discord_key )
