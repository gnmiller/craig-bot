import discord, logging
from funcs import * # bot
from discord.ext import commands
from cb_classes import cb_guild
from math import ceil

# settings
settings = get_settings( 'settings.json' )
pfx = settings['bot']['prefix']
discord_token = settings['discord']['token']
youtube_token = settings['youtube']['token']
openai_token = settings['openai']['token']
db_file = settings['bot']['db_file']
logfile = settings['bot']['logfile']

# need a better way to store/pass these around
cmds = ['help','set','get','yt']
opts = ['prof_filter']

# init
intents = discord.Intents( messages = True, presences = True, guilds = True, 
                          members = True, reactions = True, message_content = True )
#client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix=pfx,intents=intents)

# logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename=logfile, encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

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
@bot.event
async def on_ready():
    global bot_id
    global guilds
    init_db( db_file )
    bot_id = bot.user.id
    for g in bot.guilds:
        await g.me.edit(nick="BeeStingBot2.0")
        t_guild = check_guild( g, db_file )
        if not t_guild:
            t_guild = insert_guild( g, data=None, db_file=db_file )
        guilds[t_guild.guild_id] = t_guild
    print(invite_uri())
    return

cmds = ['help','set','get','yt']
opts = ['prof_filter']
@bot.event
async def on_message( msg ):
    global bot_id
    global guilds
    pinged = False
    # @ mentions block
    try:
        for m in msg.mentions:
            if m.id == bot_id:
                pinged = True
            pinged = True
        if pinged == False:
            res = await bot.process_commands(msg) # on_message() blocks the bot.commands() syntax unless we explicitly call this
            return res
        else:
            # assume we want to query openAI
            prompt = msg.content
            msg_to_edit = await msg.channel.send("```Please hold while I commune with SkyNet.```")
            oai_resp = prompt_openai( in_text=prompt, user=msg.author,
                                        openai_key=openai_token, db_file=db_file )
            await msg_to_edit.edit("```"+str(oai_resp.choices[0].message.content+"```"))
            return
    except Exception as e:
        print(e)
        return e
    
@bot.event
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

@bot.command(
        help = "Search for a YouTube video with the message as the search terms.",
        brief = "Search YouTube"
)
async def yt(ctx, *, message):
    cur_guild = guilds[ctx.guild.id]
    try:
        cur_search = cur_guild.get_search( ctx.author.id, cur_guild.guild_id )
    except RuntimeError as e:
        await ctx.send("```I think you have an existing search running. Try completing that first.```")
        return cur_search
    res = yt_search( message, youtube_token )
    #res_str = search_results_printstr( res )
    import pdb
    pdb.set_trace()
    sent_msg = await ctx.send("```Performing YouTube Search please hold.```")
    try:
        s = cur_guild.add_search( "youtube", ctx.author, message, res, sent_msg )
        send_str = "Search Terms: {}\n" \
                    "Search Results: \n"
        index = 0
        for k,v in res.items():
            index+=1
            send_str+="{}. {} -- {}\n".format(index,v,k)
        await sent_msg.edit("```{}```".format(send_str))
        pick = await bot.wait_for('message', # wait for message from same guild & author
                                     check= lambda message: message.author == ctx.author
                                                        and message.guild == ctx.guild)
        select = get_selection(pick.content)
        i = 0
        for k,v in s.data['search_results'].items():
            i+=1
            if i == select:
                cur_guild.del_search( s.get_uid(), s.get_gid() )
                await sent_msg.edit( yt_uri(k) )
                return s
        
    except RuntimeError as e:
        await sent_msg.edit("```Problem performing search.\n{}\n```".format(e))
        s = cur_guild.del_search( ctx.guild.id, ctx.author.id ) # passing IDs direct from msg here to avoid issues
        return s
    
@bot.command(
    help = "Prompt OpenAI for a response. A response limit can be specified. If none is given" \
            "The bot will assume 200 or less characters in the response to help avoid API limits." \
            "There is a hard cap of 1024 characters on any response.\n" \
            "The model can also be specified, but it is reccomended to leave this as default (gpt-3.5-turbo)" \
            "Unless you have a specific need to change it.\n" \
            "When specifying a length or prompt different from the default the 'length=' or 'name='" \
            "MUST be passed as part of the message or it will be included in the prompt to the AI.\n" \
            "This command is also available via @mentioning the bot, however model and length cannot be supplied in this way.",
    brief = "Prompt OpenAI. This command is also available via @mention.",
    usage = "!openai [len=prompt_max_length] [model=openai_model] <prompt text>",
)
async def openai(ctx, *, message):
    def_length = 200
    def_model = "gpt-3.5-turbo"
    index = 0
    length = def_length
    model = def_model
    temp = ""

    # check for params
    for i in message.split():
        if i.startswith("len") and length == def_length:
            try:
                length = i.split('=')[1]
                index+=1
            except Exception as e:
                length = def_length
        if i.startswith("model") and model == def_model:
            try:
                model = i.split('=')[1]
                index+=1
            except Exception as e:
                model = def_model
    
    # set the prompt string
    for i in message.split()[index:]:
        temp += i+" "
    prompt=temp[0:len(temp)-1]

    # commune with the elders
    msg_to_edit = await ctx.send("```Please hold while I commune with SkyNet.```")
    oai_resp = prompt_openai( in_text=prompt, user=ctx.author,
                                openai_key=openai_token, model=model,
                                max_resp_len=length, db_file=db_file )
    await msg_to_edit.edit("```"+str(oai_resp.choices[0].message.content+"```"))
    return None

@bot.command(
        help = "Roll x dice y times. To avoid spam the max number of dice is 50 and the max" \
             " number of sides is 100",
        brief = "Roll some dice",
        usage = "!roll [x] [y]\nRoll x dice y times."
)
async def roll(ctx, dice="1d20"):
    sent_msg = await ctx.send("```Rattling the dice tower, one moment please.```")
    try:
        num_d=dice.split('d')[0]
        num_s=dice.split('d')[1]
    except Exception as e:
        num_d=1
        num_s=20
    num_d = min(num_d,50)
    num_s = min(num_s,100)
    rolls = cb_roll(int(num_d),int(num_s), db_file)
    if num_d == 1:
        await sent_msg.edit("```You rolled {0} {1} with {2} sides.\nResults: {3}```".format(
        num_d,
        "die",
        num_s,
        [x[1] for x in rolls]
    ))
    else:
        await sent_msg.edit("```You rolled {0} {1} with {2} sides.\nResults: {3}\nAverage: {4}```".format(
        num_d,
        "dice",
        num_s,
        [x[1] for x in rolls],
        cb_avg(rolls)
    ))

bot.run(discord_token)
