<<<<<<< HEAD
import discord
from funcs import * # bot
from cb_classes import cb_guild
=======
import discord, asyncio, urllib3, sys, os, logging, random, string
from funcs import *
>>>>>>> dcb8e2755431b7f393fa7ddbe350149c5f63fa1c
import pdb

# settings
settings = get_settings( 'settings.json' )
pfx = settings['bot']['prefix']
discord_token = settings['discord']['token']
youtube_token = settings['youtube']['token']
openai_token = settings['openai']['token']
db_file = settings['bot']['db_file']

<<<<<<< HEAD
# need a better way to store/pass these around
cmds = ['help','set','get','yt']
opts = ['prof_filter']

# init
intents = discord.Intents( messages = True, presences = True, guilds = True, 
                          members = True, reactions = True, message_content = True )
client = discord.Client(intents=intents)
=======
intents = discord.Intents.all()

# this has never worked and i dont want to implement it
#if not discord.opus.is_loaded():
#    discord.opus.load_opus()
urllib3.disable_warnings()

client = discord.Client( intents=intents )
>>>>>>> dcb8e2755431b7f393fa7ddbe350149c5f63fa1c

# setup slash commands NYI
# tree = app_commands.CommandTree(client)

# generate a URI for inviting the bot to a server.
def invite_uri():
    if settings is None:
        raise FileNotFoundError("settings not loaded!")
    else:
        client_id = settings['discord']['app_id']
        permissions = settings['bot']['perms']
        scope = "bot%20applications.commands"
        ret = "https://discord.com/api/oauth2/authorize?client_id={}&permissions={}&scope={}".format(client_id,permissions,scope)
        return ret

bot_id = None
guilds = {}
@client.event
async def on_ready():
    global bot_id
    global guilds
    init_db( db_file )
    bot_id = client.user.id
    for g in client.guilds:
        t_guild = check_guild( g, db_file )
        guilds[t_guild.guild_id] = t_guild
        if not t_guild:
            insert_guild( g, data=None, db_file=db_file )
        else: 
            continue
    print(invite_uri())
    return

cmds = ['help','set','get','yt']
opts = ['prof_filter']
@client.event
async def on_message( msg ):
<<<<<<< HEAD
    global bot_id
    global guilds
    pinged = False
    cmd = None
    text = None
    cur_guild = guilds[msg.guild.id]

    # trying for search result
    # TODO validate the user wanted to make a selection
    # currently get_selection() doesnt care what you pass as the input
    #   it either returns 1 (default) or int() of the input
    try:
        cur_search = cur_guild.get_search( msg.author.id, cur_guild.guild_id )
    except Exception as e:
        cur_search = None    
    if not cur_search is None: # there is an active search
        # validate the user and guild are the same as the requester
        if msg.author.id == cur_search.get_uid() and msg.guild.id == int(cur_search.get_gid()):
            select = get_selection(msg.content)
            i = 0
            for k,v in cur_search.data['search_results'].items():
                i+=1
                if i == select:
                    my_id = k
                    break
            #sent_msg = getmsg(discord, cur_search.data['sent_msg'])
            sent_msg = cur_search.data['sent_msg']
            cur_guild.del_search( cur_search.get_uid(), cur_search.get_gid() )
            await sent_msg.edit( yt_uri(my_id) )
            return sent_msg
        else:
            # check if they tried to select
            # print msg they are not allowed
            return cur_search

    # prefix block
    if chk_pfx(msg.content, pfx): # this is a command wake up!
        try:
                text = slicer(msg.content,pfx) # slice off the prefix
                cmd = get_cmd( text, cmds )
                text = msg.content[len(pfx)+len(cmd)+1:len(msg.content)]
        except Exception as e:
                return e
    
        if cmd == "yt":
=======
    # check if the message was trying to retrieve a search result and transmit it
    for e in searches:
        if ( msg.author == e['msg'].author 
            and msg.channel == e['msg'].channel 
            and msg.guild == e['msg'].guild ):
>>>>>>> dcb8e2755431b7f393fa7ddbe350149c5f63fa1c
            try:
                cur_search = cur_guild.get_search( msg.author.id, cur_guild.guild_id )
            except RuntimeError as e:
                await msg.channel.send("```I think you have an existing search running. Try completing that first.```")
            res = yt_search( text, youtube_token )
            #res_str = search_results_printstr( res )
            sent_msg = await msg.channel.send("```Performing YouTube Search please hold.```")
            try:
                s = cur_guild.add_search( "youtube", msg.author, text, res, sent_msg )
                send_str = "Search Terms: {}\n" \
                            "Search Results: \n"
                index = 0
                for k,v in res.items():
                    index+=1
                    send_str+="{}. {} -- {}\n".format(index,v,k)
                await sent_msg.edit("```{}```".format(send_str))
            except RuntimeError as e:
                await sent_msg.edit("```Problem performing search.\n{}\n```".format(e))
                s = cur_guild.del_search( msg.guild.id, msg.author.id ) # passing IDs direct from msg here to avoid issues
                return s
        elif cmd == "flush":
            if msg.author.id == "147978461179281408":
                cur_guild.flush()
                return None
        else:
            # get commands
            split_text = text.split()
            opt = get_opt( split_text[1] )
            vals = []
            for i in range(2,len(split_text)):
                vals.append(i)
                cmd_data = {
                    "cmd":cmd,
                    "guild":guilds[msg.guild.id],
                    "opt":opt,
                    "vals":vals
                }
            ret = do_cmd( cmd_data["cmd"], 
                        cmd_data["opt"], 
                        cmd_data["vals"], 
                        cmd_data["guild"], 
                        db_file )
            return ret

<<<<<<< HEAD
    # @ mentions block
    try:
        for m in msg.mentions:
            if m.id == bot_id:
                pinged = True
            pinged = True
        if pinged == False:
=======
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
>>>>>>> dcb8e2755431b7f393fa7ddbe350149c5f63fa1c
            return
        else:
            # do bot stuff
            if "help" in msg.content or "usage" in msg.content and msg.content.length > 15: # need a better check to ignore real prompts
                text = print_help()
                await msg.channel.send(text)
            else:
                # assume we want to query openAI
                prompt = msg.content
                msg_to_edit = await msg.channel.send("```Please hold while I commune with SkyNet.```")
                oai_resp = prompt_openai( prompt, msg.author, openai_token, db_file )
                await msg_to_edit.edit("```"+str(oai_resp.choices[0].message.content+"```"))
                return
        return None # catch all return
    except Exception as e:
        print(e)
        return e

@client.event
async def on_guild_join( guild ):
    try:
        row = check_guild( guild, db_file )
        if row == None:
            ret = insert_guild( guild, db_file )
        else:
           ret = None
        return ret
    except FileNotFoundError as e:
        print(e)
        return None
    
async def getmsg( client, msg_id ):
    msg = await client.fetch_message(msg_id)
    return msg

client.run(discord_token)
