import discord, asyncio, urllib3, sys, os, logging
from funcs import *
##### init #####
log = setup_logs( 'craig-bot.log' )
settings = get_settings( 'settings.json' )
pfx = settings['bot']['prefix']
discord_token = settings['discord']['token']
youtube_token = settings['youtube']['token']
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

searches = []
@client.event
async def on_message( msg ):
    
    # check if the message was trying to retrieve a search result and transmit it
    for e in searches:
        if ( msg.author == e['msg'].author 
            and msg.channel == e['msg'].channel 
            and msg.guild == e['msg'].guild ):
            try:
                choice = int( msg.content )
            except:
                return
            res = e['res']
            video_uri='https://www.youtube.com/watch?v={}'.format( res[choice][1] )
            await e['sent'].edit( 
                                content='Selected Video: {}\nTitle: {}\n{}'.format( 
                                choice, res[choice][0], video_uri ) )
            searches.remove(e)

    # normal query
    if not chk_pfx( msg.content, pfx ):
        return
    else:
        # strip out the cmd for easier use
        cmd = msg.content[len(pfx):len(msg.content)]

        # youtube search
        if cmd[0:2] == 'yt':
            query = cmd[2:len(cmd)]
            query = query[1:len(query)].lower() 
            sent = await msg.channel.send( '```smalltalk\nSearching for {}...```'.format( query ) )
            t_dict = {'msg':msg, 'sent':sent, 'query':query, 'res':yt_search( query, youtube_token)}
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
client.run( discord_token )
