#!/usr/bin/env python3
# Craig-bot
# A simple Discord bot built using the Python Discord API
# https://discordpy.readthedocs.io/en/latest/api.html
# Version 0.1.0
__version__ = "Version 0.1.1"

import discord, asyncio, urllib3, sys, os, logging, random, string
from funcs import *

##### init #####
log = setup_logs( 'craig-bot.log' )
settings = get_settings( 'settings.json' )
pfx = settings['bot']['prefix']
discord_token = settings['discord']['token']
youtube_token = settings['youtube']['token']
omdb_token = settings['omdb']['token']
log = setup_logs( 'craig-bot.log' )

if not discord.opus.is_loaded():
    discord.opus.load_opus()
urllib3.disable_warnings()

client = discord.Client()

class bt_timer:
    def __init__(self, timeout, callback, msg):
        self._timeout = timeout
        self._callback = callback
        self._task = asyncio.ensure_future(self._job())
        self._msg = msg

    async def _job(self):
        await asyncio.sleep(self._timeout)
        await self._callback( self._msg )

    def cancel(self):
        self._task.cancel()

async def bt_timer_cb( msg ):
    for e in searches:
        if e[1].id == msg.id:
            await msg.edit( content='```smalltalk\nTimed out! Please try again!\n```' )
            try:
                searches.remove(e)
            except:
                pass
    return

##### bot stuff #####
@client.event
async def on_ready():
    log.debug( "begin startup process" )
    path = os.path.dirname( os.path.realpath( __file__ ))
    with open( path + '/var/bot.pid', mode='w' ) as pid_file:
        pid_file.write( str(os.getpid()) )
        pid_file.close()
    return 0

searches = [] # this shouldnt be global but...
@client.event
async def on_message( msg ):

    # check if the message was trying to retrieve a search result and transmit it
    for e in searches:
        if ( msg.author == e['msg'].author 
            and msg.channel == e['msg'].channel 
            and msg.guild == e['msg'].guild ):
            try:
                choice = int( msg.content ) - 1
            except:
                return
            if e['kind'] == 'youtube':
                res = e['res']
                video_uri='https://www.youtube.com/watch?v={}'.format( res[choice][1] )
                await e['sent'].edit( 
                                    content='Selected Video: {}\nTitle: {}\n{}'.format( 
                                    choice, res[choice][0], video_uri ) )
                searches.remove(e)
            elif e['kind'] == 'omdb':
                res = e['res']
                imdb_uri ='https://www.imdb.com/title/{}/'.format( res[choice][2] )
                await e['sent'].edit( content='Selected: {} ({})\n{}'.format( res[choice][0], res[choice][1], imdb_uri ) )
                searches.remove(e)
            return

    # normal query
    if not chk_pfx( msg.content, pfx ):
        return
    else:
        # strip out the cmd for easier use
        cmd = msg.content[len(pfx):len(msg.content)]

        # help!
        if ck_cmd( cmd, 'help' ) or ck_cmd( cmd, 'h' ):
            await msg.author.send( '```{}```'.format( help() ) )
            return

        # youtube search
        if ck_cmd( cmd, 'yt' ):
            query = cmd[2:len(cmd)]
            query = query[1:len(query)].lower() 
            sent = await msg.channel.send( '```smalltalk\nSearching for {}...```'.format( query ) )
            t_dict = {'msg':msg, 'sent':sent, 'query':query, 'res':yt_search( query, youtube_token ), 'kind':'youtube' }
            searches.append(t_dict)
            send_str = '```smalltalk\nPlease select a video:```\n```smalltalk\n'
            count = 0
            for e in t_dict['res']:
                send_str += '{}. {}\n'.format( count+1, t_dict['res'][count][0] )
                count+=1
            send_str += '```\n'
            await sent.edit( content=send_str )
            t = bt_timer( 10, bt_timer_cb, sent ) # set a timeout for 10 seconds
            return

        # omdb search
        # happily both commands are 4 chars so we can stay lazy
        if ck_cmd( cmd, 'omdb' ) or ck_cmd( cmd, 'imdb' ):
            query = cmd[4:len(cmd)]
            query = query[1:len(query)].lower()
            sent = await msg.channel.send( '```smalltalk\nSearching for {}...```'.format( query ) )
            t_dict = {'msg':msg, 'sent':sent, 'query':query, 'res':omdb_search( query, omdb_token ), 'kind':'omdb' }
            try:
                if t_dict['res'] <= 0:
                    await sent.edit( "```No results return for search (Query: {}). Please try again.```".format( query ) )
                    return
            except TypeError:
                pass
            searches.append(t_dict)
            send_str = '```smalltalk\nPlease select a result:```\n```smalltalk\n'
            count = 0
            for e in t_dict['res']:
                send_str += '{}. {} ({})\n'.format( count+1, t_dict['res'][count][0], t_dict['res'][count][1] )
                count+=1
            send_str+='```\n'
            await sent.edit( content=send_str )
            t = bt_timer( 10, bt_timer_cb, sent ) # 10 sec timeout...
            return
        
        # dice roll
        if ck_cmd( cmd, 'roll' ):
            try:
                temp = msg.content[ len( "!roll "):len(msg.content) ].split( 'd', 2 )
                if len(temp) != 2:
                    await msg.channel.send( '```Incorrect format. Try again with the following format: XdY.```' )
                int( temp[0] )
                int( temp[1] )
            except:
                await msg.channel.send( '```Incorrect format. Try again with the following format: XdY.```' )
                return
            output = []
            for i in range( 0, int(temp[0]) ):
                output.append( random.randint( 1, int(temp[1]) ) )
            await msg.channel.send( '```Rolled {} {}-sided dice and got the following results: {}```'.format(
                                    temp[0], temp[1], output ) )
            return

        # alt caps
        if ck_cmd( cmd, 'alt' ):
            try:
                conv = msg.content[len( "!alt " ):len(msg.content)].upper()
                count = 0
                out = ''
                for c in conv:
                    if c not in string.ascii_letters:
                        out+=c
                        continue
                    if count%2 == 0:
                        out+=c
                    else:
                        out+=c.lower()
                    count+=1

                await msg.channel.send( '```{}```'.format( str(out ) ) )
            except:
                return
            return
client.run( discord_token )
