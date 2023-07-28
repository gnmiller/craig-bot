import discord, openai # needed
import asyncio, urllib3, sys, os, logging, random, string, json, sqlite3# maybe no longer needed
from funcs import * # bot
from cb_guild import cb_guild as cb_guild
import pdb # remove in prod

# settings
settings = get_settings( 'settings.json' )
pfx = settings['bot']['prefix']
discord_token = settings['discord']['token']
youtube_token = settings['youtube']['token']
openai_token = settings['openai']['token']
db_file = settings['bot']['db_file']

# these should not be globals...
cmds = ['help','set','get']
opts = ['prof_filter']

# init bot and openai
openai.api_key = openai_token
intents = discord.Intents( messages = True, presences = True, guilds = True, members = True, reactions = True )
client = discord.Client(intents=intents)

# setup slash commands NYI
# tree = app_commands.CommandTree(client)

def invite_uri():
    if settings == None:
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
    print( "ready!" )
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
    print("My Discord ID: {}".format(bot_id))
    return

@client.event
async def on_message( msg ):
    global bot_id
    global guilds
    global cmds
    global opts
    pinged = False

    # prefix block
    try:
        if msg.content[0:len(pfx)] is pfx: # this is a command wake up!
            text = msg.content[len(pfx)+2:len(msg.content)] # slice off the prefix
            cmd = get_cmd( text )
            if cmd is None:
                await msg.channel.send("huh?")
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
    except Exception as e:
        return None
    
    # @ mentions block
    try:
        for m in msg.mentions:
            print("caught my ID setting pinged true")
            if m.id == bot_id:
                pinged = True
            pinged = True
        if pinged == False:
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
                oai_resp = prompt_openai( prompt, openai_token )
                await msg_to_edit.edit("```"+str(oai_resp.choices[0].message.content+"```"))
                return
        return None # catch all return
    except Exception as e:
        return None

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

client.run(discord_token)
