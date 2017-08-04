#!/usr/bin/python3.6

import discord, asyncio, pytz, datetime, os, json
from funcs import get_got_time, magic_8ball, help_str, write_auth, bs_now as bnow
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
max_msg = settings["bot"]["stored_msg"]
date_str = "%m/%d/%y %I:%M %p"
f.close()

servers = []
@client.event
async def on_ready():
    for s in client.servers:
        servers.append( bs_server( client, s, timeout_val, max_msg ) )
    await client.change_presence( game=discord.Game( name="indev build" ) )
    print( "startup finished\n" )
    
@client.event
async def on_server_join( server ):
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
    now = bnow()
    p = msg.content[:len(prefix)]
    args = msg.content[len(prefix):].split()
    if p == prefix:
        args[0] = args[0].lower()
        cur_serv.queue_cmd( msg )
        if args[0] == "help" or args[0] == "h":
            await( client.send_message( msg.author, help_str( prefix ) ))
            return
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
        if args[0] == "8ball":
            if len( args ) < 2:
                await client.send_message( msg.channel, "You need to ask a question!\n" )
                return
            temp = magic_8ball()
            p_str = "```smalltalk\nYou asked: {}\nThe Magic 8-Ball says: {}```\n".format( msg.content[7:], temp )
            await client.send_message( msg.channel, p_str )
            return
        if args[0] == "status":
            al = cur_serv.get_auth( msg.author )
            if al > 3:
                my_pid = os.getpid()
                created = os.path.getmtime( "/proc/"+str(my_pid) )
                creat_str = "```smalltalk\nBot running with PID "+str(my_pid)+" since "
                creat_str += datetime.datetime.fromtimestamp( int(created) ).strftime( date_str )
                creat_str += "```\n"
                await client.send_message( msg.channel, creat_str )
                return
            else:
                await client.send_message( msg.channel, "You are not authorized for this command. Required: 3 ({})\n".format( str( al ) ) )
                return
        if args[0] == "set_game":
            al = cur_serv.get_auth( msg.author )
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
            al = cur_serv.get_auth( msg.author )
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
            al = cur_serv.get_auth( msg.author )
            if len( args ) <= 2:
                await client.send_message( msg.channel, "```Usage: {}add <@user> <level>```".format( prefix ) )
                return
            if al < int(args[2]):
                await client.send_message( msg.channel, "```You cannot add a user with higher auth level than yourself!```" )
                return
            uid = args[1][3:-1]
            for u in cur_serv.users:
                if cur_serv.users[u].user.id == uid:
                    cur_serv.add_auth( u.me, level )
                    await client.send_message( msg.channel, "```Adding {} to the current server's auth list at level {}.\n```".format( args[1], args[2] ) )
                    return
            await client.send_message( msg.channel, "```Failed to add {} to the current server's auth list.".format( args[1] ))
            return
            print( "asdf" )
        if args[0] == "eval":
            func = ""
            ops = [ '+', '-', '/', '*', '%' ]
            pdb.set_trace()
            for i in range( 1, len(args) ):
                for c in args[i]:
                    if c in ops or c.isdigit():
                        func += c
                    else:
                        await client.send_message( msg.channel, "This is only a basic calculator!\n" )
                        return
            ret = eval( func )
            await client.send_message( msg.channel, "```Evaluated: {}\nResult: {}\n```".format( func, ret ) )
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
    msg_str = "```smalltalk\nUsername: {}\nID: {}\nAuth Level: {}\n```".format( msg.author.name, msg.author.id, serv.get_auth( msg.author ) )
    serv.queue_cmd( msg )
    return await client.send_message( msg.channel, msg_str )

client.run( discord_key )
